# graph/feedback_graph.py
# 실제 API 흐름을 LangGraph로 구성:
#   START → retrieve(DB+RAG) → generate(프롬프트+LLM) → review(품질검토)
#         → decide: 통과 END / 불량이고 재시도 여력 있으면 retrieve로 되돌아감
# 라우터(feedbacks_router.py)가 이 graph를 invoke 한다. (더 이상 데모/가짜값 아님)

import json
import logging
from typing import TypedDict, Optional, Any, List

from langgraph.graph import StateGraph, START, END
from pydantic import ValidationError
from sqlalchemy import desc

from models import LessonRecord, Child
from rag.rag_service import rag_search
from prompt_service import build_prompt
from llm_service import generate_feedback
from schemas import FeedbackLLMOut

logger = logging.getLogger("feedbacks")

# review가 확인할 최소 품질 조건
REQUIRED = ["next_goal", "teacher_feedback", "parent_feedback"]
MAX_ATTEMPTS = 2   # 재시도 최대 횟수 (무한루프 방지 가드)


# ── State: 단계 사이에서 들고 다니는 데이터 가방 ──
class FeedbackState(TypedDict):
    db: Any                        # DB 세션 (노드들이 조회에 사용)
    run_id: str                    # 요청 추적 꼬리표 (로그용)
    lesson_record_id: int
    child: Optional[Any]
    records: Optional[List[Any]]
    rag_context: Optional[str]
    feedback: Optional[dict]
    review_ok: Optional[bool]
    attempts: Optional[int]
    error_type: Optional[str]      # 실패 유형 꼬리표 (json_parse_error / schema_validation_error / llm_call_error)
    error_detail: Optional[str]    # 사람이 읽을 실패 설명 (개인정보 제외)


# ── 1) retrieve: DB에서 아이+기록 조회 + RAG 검색 ──
def retrieve(state: FeedbackState) -> dict:
    db = state["db"]
    run_id = state["run_id"]
    record = db.query(LessonRecord).filter(LessonRecord.id == state["lesson_record_id"]).first()
    child = db.query(Child).filter(Child.id == record.child_id).first()
    logger.info("[%s] child loaded - %s", run_id, child.name)

    question = f"질문: {child.personality} 아이가 {record.activity}를 했을 때 뭐라고 말해주나요?"
    found = rag_search(question)
    logger.info("[%s] RAG search completed", run_id)

    records = (
        db.query(LessonRecord)
        .filter(LessonRecord.child_id == child.id)
        .order_by(desc(LessonRecord.lesson_date))
        .limit(5)
        .all()
    )
    return {"child": child, "records": records, "rag_context": found}


# ── 2) generate: 프롬프트 조립 + LLM 호출 + JSON 파싱 + 스키마 검증 ──
def generate(state: FeedbackState) -> dict:
    run_id = state["run_id"]
    attempts = (state.get("attempts") or 0) + 1
    prompt = build_prompt(state["child"], state["records"], state["rag_context"])

    feedback = None
    error_type = None
    error_detail = None

    # (a) LLM 호출 자체가 실패할 수 있다 (네트워크/쿼터 등) → 그래프를 죽이지 말고 실패로 기록
    try:
        result = generate_feedback(prompt)
    except Exception as e:
        error_type = "llm_call_error"
        error_detail = type(e).__name__
        logger.warning("[%s] LLM 호출 실패 (attempt %d) - %s", run_id, attempts, error_detail)
        return {"feedback": None, "attempts": attempts,
                "error_type": error_type, "error_detail": error_detail}

    # (b) JSON 파싱 오류 구분
    try:
        parsed = json.loads(result)
    except (json.JSONDecodeError, TypeError):
        error_type = "json_parse_error"
        error_detail = "LLM 응답이 올바른 JSON이 아님"
        logger.warning("[%s] JSON 파싱 실패 (attempt %d)", run_id, attempts)
        return {"feedback": None, "attempts": attempts,
                "error_type": error_type, "error_detail": error_detail}

    # (c) 필수 필드 누락 / 빈 문자열 / 타입 오류 구분 (Pydantic)
    try:
        validated = FeedbackLLMOut.model_validate(parsed)
    except ValidationError as e:
        error_type = "schema_validation_error"
        # 개인정보가 섞이지 않도록 '어떤 필드가 왜 틀렸는지'만 남긴다 (값 자체는 로깅 X)
        error_detail = "; ".join(
            f"{'.'.join(str(p) for p in err['loc'])}:{err['type']}" for err in e.errors()
        )
        logger.warning("[%s] 스키마 검증 실패 (attempt %d) - %s", run_id, attempts, error_detail)
        return {"feedback": None, "attempts": attempts,
                "error_type": error_type, "error_detail": error_detail}

    feedback = validated.model_dump()
    logger.info("[%s] LLM generation OK (attempt %d)", run_id, attempts)
    return {"feedback": feedback, "attempts": attempts,
            "error_type": None, "error_detail": None}


# ── 3) review: 검증을 통과한 feedback이 실제로 들어있는지 확인 ──
def review(state: FeedbackState) -> dict:
    run_id = state["run_id"]
    fb = state.get("feedback") or {}
    # generate에서 이미 Pydantic 검증을 통과한 것만 feedback에 담기므로,
    # 여기서는 '값이 존재하는가'로 최종 확정한다. (이중 안전장치로 REQUIRED도 확인)
    ok = bool(fb) and all(key in fb and fb[key] for key in REQUIRED)
    logger.info("[%s] review - 저장 가능? %s", run_id, ok)
    return {"review_ok": ok}


# ── 분기 판단: 통과/재시도/최종 실패 ──
def decide(state: FeedbackState) -> str:
    if state.get("review_ok"):
        return "end"
    if (state.get("attempts") or 0) >= MAX_ATTEMPTS:
        # 한도 초과 → review_ok=False인 채로 종료. 라우터가 이걸 보고 저장을 거부한다.
        logger.warning("[%s] 재시도 한도(%d) 초과 → 최종 실패(저장 안 함), type=%s",
                       state["run_id"], MAX_ATTEMPTS, state.get("error_type"))
        return "end"
    return "retry"


# ── 그래프 조립 ──
builder = StateGraph(FeedbackState)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_node("review", review)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", "review")
builder.add_conditional_edges("review", decide, {"end": END, "retry": "retrieve"})

graph = builder.compile()
