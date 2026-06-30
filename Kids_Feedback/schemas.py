from pydantic import BaseModel


from datetime import date, datetime
from typing import Optional

class ChildCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    level: Optional[str] = None
    memo: Optional[str] = None

    memory_hint: Optional[str] = None
    personality: Optional[str] = None
    preferred_feedback: Optional[str] = None
    caution_note: Optional[str] = None
    material_note: Optional[str] = None
    teacher_memo: Optional[str] = None


class ChildUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    level: Optional[str] = None
    memo: Optional[str] = None

    memory_hint: Optional[str] = None
    personality: Optional[str] = None
    preferred_feedback: Optional[str] = None
    caution_note: Optional[str] = None
    material_note: Optional[str] = None
    teacher_memo: Optional[str] = None


class ChildResponse(ChildCreate):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LessonRecordCreate(BaseModel):
    child_id: int
    lesson_date: date
    activity: Optional[str] = None
    performance: Optional[str] = None
    attitude: Optional[str] = None
    difficulty: Optional[str] = None
    teacher_note: Optional[str] = None


class LessonRecordResponse(LessonRecordCreate):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

#ChildCreate = 사용자가 POST로 보내는 데이터
#ChildResponse = 서버가 응답으로 돌려주는 데이터


# 사용자는 "어느 수업 기록으로 피드백 만들래?"만 보낸다 → lesson_record_id 하나
class FeedbackGenerate(BaseModel):
    lesson_record_id: int

# FeedbackResponse(저장 후 응답용)는 세션 5에서 만든다.

