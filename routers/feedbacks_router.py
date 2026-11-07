## 피드백 생성: lesson_record_id 받아 → 아이/기록 꺼내 → 프롬프트 → LLM → 결과 반환

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models import LessonRecord, Feedback
from schemas import FeedbackGenerate, FeedbackResponse
from graph.feedback_graph import graph as feedback_graph   # ★ 직선 코드 대신 LangGraph 흐름 사용

import logging
import uuid
import time

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
     

@router.get("/{child_id}",response_model= List[FeedbackResponse])
def get_feedbacks(child_id: int, db: Session = Depends(get_db)):
    feedbacks = db.query(Feedback).filter(Feedback.child_id == child_id).all()

    # 이 아이 피드백이 하나도 없으면 → 빈 리스트 대신 404로 "없다"고 알려주기
    if not feedbacks:
        raise HTTPException(status_code=404, detail="해당 아이의 피드백이 없습니다")

    return feedbacks




    


