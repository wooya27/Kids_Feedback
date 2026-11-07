# graph/feedback_graph.py
# 실제 API 흐름을 LangGraph로 구성:
#   START → retrieve(DB+RAG) → generate(프롬프트+LLM) → review(품질검토)
#         → decide: 통과 END / 불량이고 재시도 여력 있으면 retrieve로 되돌아감
# 라우터(feedbacks_router.py)가 이 graph를 invoke 한다. (더 이상 데모/가짜값 아님)

import json
import logging
from typing import TypedDict, Optional, Any, List

from langgraph.graph import StateGraph, START, END
from sqlalchemy import desc

from models import LessonRecord, Child
from rag.rag_service import rag_search
from prompt_service import build_prompt
from llm_service import generate_feedback

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


# ── 2) generate: 프롬프트 조립 + LLM 호출 + JSON 파싱 ──
def generate(state: FeedbackState) -> dict:
    run_id = state["run_id"]
    attempts = (state.get("attempts") or 0) + 1
    prompt = build_prompt(state["child"], state["records"], state["rag_context"])
    result = generate_feedback(prompt)
    feedback = json.loads(result)
    logger.info("[%s] LLM generation completed (attempt %d)", run_id, attempts)
    return {"feedback": feedback, "attempts": attempts}


# ── 3) review: 필수 필드가 다 있고 빈 값이 아닌지 검토 ──
def review(state: FeedbackState) -> dict:
    run_id = state["run_id"]
    fb = state.get("feedback") or {}
    ok = all(key in fb and fb[key] for key in REQUIRED)
    logger.info("[%s] review - 필수필드 통과? %s", run_id, ok)
    return {"review_ok": ok}


# ── 분기 판단: 통과/재시도/포기 ──
def decide(state: FeedbackState) -> str:
    if state.get("review_ok"):
        return "end"
    if (state.get("attempts") or 0) >= MAX_ATTEMPTS:
        logger.warning("[%s] review 재시도 한도 초과 → best-effort 저장", state["run_id"])
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
