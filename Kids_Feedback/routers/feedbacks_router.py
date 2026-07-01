## 피드백 생성: lesson_record_id 받아 → 아이/기록 꺼내 → 프롬프트 → LLM → 결과 반환

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import LessonRecord, Child, Feedback
from schemas import FeedbackGenerate, FeedbackResponse
from prompt_service import build_prompt
from llm_service import generate_feedback
import json

router = APIRouter(
    prefix="/feedbacks",
    tags=["feedbacks"]
)


@router.post("/generate")  # 피드백 "생성" (저장은 세션 5)
def generate_feedback_endpoint(payload: FeedbackGenerate, db: Session = Depends(get_db)):
    # 1) 받은 lesson_record_id로 그 수업 기록 1개 찾기
    record = db.query(LessonRecord).filter(LessonRecord.id == payload.lesson_record_id).first()

    # 1-2) 없는 lesson_record_id면 record가 None → 아래서 크래시 나기 전에 404로 막기
    if record is None:
        raise HTTPException(status_code=404, detail="해당 수업 기록이 없습니다")

    # 2) 그 기록이 어느 아이 건지 → child_id로 아이 찾기
    child = db.query(Child).filter(Child.id == record.child_id).first()

    # 3) 그 아이의 최근 수업 기록 5개 (Day 3에서 한 거랑 같은 쿼리)
    records = db.query(LessonRecord).filter(LessonRecord.child_id == child.id).order_by(desc(LessonRecord.lesson_date)).limit(5).all()

    # ── 여기 빈칸 2개를 네가 채워 (함수 호출 연습!) ──
    # 4) 프롬프트 조립: build_prompt에 아이(child)랑 기록들(records)을 넘겨라
    prompt = build_prompt(child, records)
    # 5) LLM 호출: generate_feedback에 위에서 만든 prompt를 넘겨라
    result = generate_feedback(prompt)

    # 6) 일단 결과 그대로 반환 (DB 저장은 세션 5)
    data = json.loads(result)
    new_feedback = Feedback(
    child_id =child.id,
    lesson_record_id =record.id,

    next_goal=data["next_goal"],          # ← data에서 꺼내 채워
    teacher_feedback=data["teacher_feedback"],   # ←
    parent_feedback=data["parent_feedback"]   # ←
     )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback
     

@router.get("/{child_id}",response_model= List[FeedbackResponse])
def get_feedbacks(child_id: int, db: Session = Depends(get_db)):
    feedbacks = db.query(Feedback).filter(Feedback.child_id == child_id).all()

    # 이 아이 피드백이 하나도 없으면 → 빈 리스트 대신 404로 "없다"고 알려주기
    if not feedbacks:
        raise HTTPException(status_code=404, detail="해당 아이의 피드백이 없습니다")

    return feedbacks




    


