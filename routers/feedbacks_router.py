## 피드백 생성: lesson_record_id 받아 → 아이/기록 꺼내 → 프롬프트 → LLM → 결과 반환

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models import LessonRecord, Feedback
from schemas import FeedbackGenerate, FeedbackResponse, FeedbackReviewUpdate
from graph.feedback_graph import graph as feedback_graph   # ★ 직선 코드 대신 LangGraph 흐름 사용

import logging
import uuid
import time
from datetime import datetime, timezone

# 강사가 내릴 수 있는 검수 결과(이 3개만 허용)
ALLOWED_REVIEW_STATUS = {"approved", "edited", "rejected"}

# 유효한 상태 전이 규칙: 현재 상태 → 허용되는 다음 상태
# approved/rejected는 '확정'이라 잠근다(재검수 금지). edited는 다시 손볼 수 있음.
ALLOWED_TRANSITIONS = {
    "pending": {"approved", "edited", "rejected"},
    "edited": {"approved", "edited", "rejected"},
    "approved": set(),
    "rejected": set(),
}

# 이 파일(라우터) 전용 로거. 이름표 "feedbacks" 로 찍힘
logger = logging.getLogger("feedbacks")

router = APIRouter(
    prefix="/feedbacks",
    tags=["feedbacks"]
)


@router.post("/generate")  # 피드백 "생성" (저장은 세션 5)
def generate_feedback_endpoint(payload: FeedbackGenerate, db: Session = Depends(get_db)):
    # run_id = 이 요청 하나를 처음~끝까지 묶어 추적하는 "꼬리표" (8자리)
    run_id = uuid.uuid4().hex[:8]
    started = time.perf_counter()  # 응답시간 재기 시작
    logger.info("[%s] feedback request received - lesson_record_id=%s", run_id, payload.lesson_record_id)

    # 1) 없는 lesson_record_id면 404로 먼저 막기 (그래프 들어가기 전)
    record = db.query(LessonRecord).filter(LessonRecord.id == payload.lesson_record_id).first()
    if record is None:
        logger.warning("[%s] STOPPED at DB lookup - lesson record not found", run_id)
        raise HTTPException(status_code=404, detail="해당 수업 기록이 없습니다")
    logger.info("[%s] lesson record loaded", run_id)

    # 2) ★ LangGraph 실행: retrieve(DB+RAG) → generate(LLM) → review(조건분기) ★
    #    예전엔 여기서 직선으로 다 했지만, 이제 그래프가 그 단계들을 담당한다.
    final = feedback_graph.invoke({
        "db": db,
        "run_id": run_id,
        "lesson_record_id": payload.lesson_record_id,
    })
    logger.info("[%s] LangGraph completed - review_ok=%s, attempts=%s",
                run_id, final.get("review_ok"), final.get("attempts"))

    # 2-1) ★ 안전장치: 검증을 최종 통과(review_ok is True)하지 못하면 저장하지 않는다 ★
    #      잘못된 JSON·필수필드 누락·재시도 한도 초과 등은 여기서 걸러져 DB 신규 행 0건.
    if final.get("review_ok") is not True:
        elapsed = time.perf_counter() - started
        logger.warning(
            "[%s] generation FAILED (NOT saved) - type=%s, attempts=%s, elapsed=%.2fs",
            run_id, final.get("error_type"), final.get("attempts"), elapsed,
        )
        raise HTTPException(
            status_code=502,  # 업스트림(LLM) 생성 실패 → 저장 거부
            detail={
                "error": "feedback_generation_failed",
                "error_type": final.get("error_type"),
                "error_detail": final.get("error_detail"),
                "attempts": final.get("attempts"),
                "run_id": run_id,
            },
        )

    # 3) 그래프 결과(final 가방)에서 피드백 꺼내 Feedback 테이블에 저장 (검증 통과분만 도달)
    data = final["feedback"]
    new_feedback = Feedback(
        child_id=final["child"].id,
        lesson_record_id=record.id,
        next_goal=data["next_goal"],
        teacher_feedback=data["teacher_feedback"],
        parent_feedback=data["parent_feedback"],
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    elapsed = time.perf_counter() - started  # 총 걸린 시간(초)
    logger.info("[%s] feedback saved - id=%s, elapsed=%.2fs", run_id, new_feedback.id, elapsed)
    return new_feedback
     

@router.patch("/{feedback_id}/review", response_model=FeedbackResponse)
def review_feedback(feedback_id: int, payload: FeedbackReviewUpdate, db: Session = Depends(get_db)):
    """강사가 AI 피드백을 검수한 결과(승인/수정/거절)를 DB에 기록한다."""
    # 1) 허용된 상태값인지 먼저 검사 (approved/edited/rejected 외엔 거부)
    if payload.review_status not in ALLOWED_REVIEW_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"review_status는 {ALLOWED_REVIEW_STATUS} 중 하나여야 합니다",
        )

    # 2) 대상 피드백 찾기 (없으면 404)
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="해당 피드백이 없습니다")

    # 2-1) 유효한 상태 전이인지 검사 (확정된 건 재검수 금지)
    current = feedback.review_status or "pending"
    if payload.review_status not in ALLOWED_TRANSITIONS.get(current, set()):
        raise HTTPException(
            status_code=409,
            detail=f"'{current}' 상태에서 '{payload.review_status}'로 바꿀 수 없습니다",
        )

    # 2-2) edited면 수정 본문을 반드시 1개 이상 받아야 한다 (원본은 보존)
    edited_fields = [payload.edited_next_goal, payload.edited_teacher_feedback,
                     payload.edited_parent_feedback]
    if payload.review_status == "edited" and not any(f and f.strip() for f in edited_fields):
        raise HTTPException(
            status_code=400,
            detail="edited 상태에는 수정 본문(edited_*)을 최소 1개 보내야 합니다",
        )

    # 3) 검수 결과 기록 + 검수 시각 도장 찍기
    feedback.review_status = payload.review_status
    feedback.review_comment = payload.review_comment
    feedback.reviewed_at = datetime.now(timezone.utc)

    if payload.review_status == "edited":
        # 보낸 수정 본문만 저장. 안 보낸 필드는 원본을 복사해 '최종 수정본'을 완성한다.
        feedback.edited_next_goal = payload.edited_next_goal or feedback.next_goal
        feedback.edited_teacher_feedback = payload.edited_teacher_feedback or feedback.teacher_feedback
        feedback.edited_parent_feedback = payload.edited_parent_feedback or feedback.parent_feedback

    db.commit()
    db.refresh(feedback)
    logger.info("feedback reviewed - id=%s, %s→%s", feedback.id, current, feedback.review_status)
    return feedback


@router.get("/{feedback_id}/final")
def get_final_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """승인 전에는 학부모용 최종본을 내보내지 않는다(전달 차단).
    - approved → 원본을 최종본으로
    - edited   → 수정본을 최종본으로
    - pending/rejected → 409 (아직/영영 전달 불가)
    원본·수정본·최종본을 서로 다른 값으로 조회할 수 있게 함께 돌려준다.
    """
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="해당 피드백이 없습니다")

    status = feedback.review_status or "pending"
    if status == "approved":
        final = {"next_goal": feedback.next_goal,
                 "teacher_feedback": feedback.teacher_feedback,
                 "parent_feedback": feedback.parent_feedback}
    elif status == "edited":
        final = {"next_goal": feedback.edited_next_goal,
                 "teacher_feedback": feedback.edited_teacher_feedback,
                 "parent_feedback": feedback.edited_parent_feedback}
    else:  # pending / rejected → 전달 차단
        raise HTTPException(
            status_code=409,
            detail=f"'{status}' 상태에서는 최종본을 전달할 수 없습니다(승인 전/거절)",
        )

    return {
        "feedback_id": feedback.id,
        "review_status": status,
        "original_draft": {"next_goal": feedback.next_goal,
                           "teacher_feedback": feedback.teacher_feedback,
                           "parent_feedback": feedback.parent_feedback},
        "final": final,
    }


@router.get("/{child_id}",response_model= List[FeedbackResponse])
def get_feedbacks(child_id: int, db: Session = Depends(get_db)):
    feedbacks = db.query(Feedback).filter(Feedback.child_id == child_id).all()

    # 이 아이 피드백이 하나도 없으면 → 빈 리스트 대신 404로 "없다"고 알려주기
    if not feedbacks:
        raise HTTPException(status_code=404, detail="해당 아이의 피드백이 없습니다")

    return feedbacks




    


