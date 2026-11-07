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

    # 3) 그래프 결과(final 가방)에서 피드백 꺼내 Feedback 테이블에 저장
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

    # 3) 검수 결과 기록 + 검수 시각 도장 찍기
    feedback.review_status = payload.review_status
    feedback.review_comment = payload.review_comment
    feedback.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(feedback)
    logger.info("feedback reviewed - id=%s, status=%s", feedback.id, feedback.review_status)
    return feedback


@router.get("/{child_id}",response_model= List[FeedbackResponse])
def get_feedbacks(child_id: int, db: Session = Depends(get_db)):
    feedbacks = db.query(Feedback).filter(Feedback.child_id == child_id).all()

    # 이 아이 피드백이 하나도 없으면 → 빈 리스트 대신 404로 "없다"고 알려주기
    if not feedbacks:
        raise HTTPException(status_code=404, detail="해당 아이의 피드백이 없습니다")

    return feedbacks




    


