# graph/feedback_graph.py
# DAY2 목표: 직선 흐름을 "검색 → 생성 → 검토" 로 나누고, 조건 분기 1개 경험
#   START → retrieve → generate → review → (정상? END : 다시 retrieve)
# 지금은 "흐름이 조건에 따라 바뀌는 것"이 목표. 진짜 DB/RAG/LLM은 다음에.

from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, START, END


# ── 1) State: 단계 사이에서 들고 다니는 "데이터 가방" ──────────────
class FeedbackState(TypedDict):
    lesson_record_id: int
    child: Optional[dict]
    records: Optional[list]
    rag_context: Optional[str]
    feedback: Optional[dict]      # 피드백 JSON (next_goal / teacher_feedback / parent_feedback)
    review_ok: Optional[bool]     # review 노드의 판정 결과
    attempts: Optional[int]       # 생성 시도 횟수 (분기 실습 + 무한루프 방지용)


# review가 확인할 "최소 품질 조건" = 이 3개 필드가 다 있는가?
REQUIRED = ["next_goal", "teacher_feedback", "parent_feedback"]


# ── 2) Node들: state를 받아 "바꿀 칸만" dict로 돌려준다 ─────────────
def retrieve(state: FeedbackState) -> dict:
    print("retrieve 실행 - lesson_record_id:", state["lesson_record_id"])
    return {"rag_context": "임시 지도 기준 (다음 작업에서 실제 RAG 연결)"}


def generate(state: FeedbackState) -> dict:
    # attempts: 없으면 0으로 보고 +1. 1차는 일부러 불량, 2차는 정상 → 분기 실습용
    attempts = (state.get("attempts") or 0) + 1
    print(f"generate 실행 (attempt {attempts})")

    if attempts == 1:
        # 1차: parent_feedback 일부러 빠뜨림 → review 탈락시키기
        feedback = {
            "next_goal": "이단뛰기 10회",
            "teacher_feedback": "집중력이 좋아졌어요",
        }
    else:
        # 2차: 3개 다 채움 → review 통과
        feedback = {
            "next_goal": "이단뛰기 10회",
            "teacher_feedback": "집중력이 좋아졌어요",
            "parent_feedback": "오늘도 즐겁게 참여했어요",
        }
    return {"feedback": feedback, "attempts": attempts}


def review(state: FeedbackState) -> dict:
    fb = state.get("feedback") or {}
    # 최소 기준: feedback이 있고 + 필수 필드 3개가 전부 있는가?
    ok = all(key in fb for key in REQUIRED)
    print("review 실행 - 필수필드 통과?", ok, "/ 가진 필드:", list(fb.keys()))
    return {"review_ok": ok}


# ── 2-b) 판단 함수: review 결과를 보고 "다음에 어디로"를 문자열로 돌려줌 ──
def decide(state: FeedbackState) -> str:
    if state.get("review_ok"):
        return "end"      # 통과 → 끝으로
    return "retry"        # 탈락 → 다시 검색부터


# ── 3) 그래프 조립 ────────────────────────────────────────────────
builder = StateGraph(FeedbackState)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_node("review", review)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", "review")       # 생성 다음엔 항상 검토

# ★ 조건 분기: review 다음은 decide() 결과에 따라 갈린다
builder.add_conditional_edges(
    "review",
    decide,
    {"end": END, "retry": "retrieve"},        # "end"면 끝, "retry"면 retrieve로 되돌아감
)

graph = builder.compile()


# ── 4) 직접 실행 테스트 ────────────────────────────────────────────
if __name__ == "__main__":
    result = graph.invoke({"lesson_record_id": 1})
    print("최종 가방:", result)
