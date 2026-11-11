from pydantic import BaseModel, field_validator


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
# 강사가 저장된 피드백을 조회할 때 화면에 뭐가 보여야 하나?


class FeedbackGenerate(BaseModel):   # 형제 1 (입력용): 왼쪽 끝
    lesson_record_id: int


class FeedbackLLMOut(BaseModel):
    """LLM(Gemini)이 돌려준 JSON을 '저장해도 되는 품질'인지 검사하는 관문.
    - 세 필드가 모두 있어야 하고(필수 필드 누락 차단)
    - 각 필드는 문자열이어야 하며(타입 오류 차단)
    - 공백만 있거나 빈 문자열이면 거절한다(빈 값 차단).
    model_validate()에서 걸리면 ValidationError가 나고,
    graph.generate가 그걸 잡아 '검증 실패'로 처리한다 → DB 저장 안 됨.
    """
    next_goal: str
    teacher_feedback: str
    parent_feedback: str

    @field_validator("next_goal", "teacher_feedback", "parent_feedback")
    @classmethod
    def not_blank(cls, v: str) -> str:
        # pydantic이 타입(str) 검사는 이미 해줌. 여기선 '내용이 비었는가'를 추가로 막는다.
        if v is None or not str(v).strip():
            raise ValueError("빈 문자열/공백만 있음")
        return str(v).strip()


class FeedbackReviewUpdate(BaseModel):   # 강사가 검수 결과를 보낼 때 쓰는 입력
    review_status: str                   # approved / edited / rejected
    review_comment: Optional[str] = None # 수정/거절 이유 메모 (선택)
    # edited 상태일 때 강사가 고친 본문(원본은 그대로 보존됨). 최소 1개는 채워야 함.
    edited_next_goal: Optional[str] = None
    edited_teacher_feedback: Optional[str] = None
    edited_parent_feedback: Optional[str] = None


class FeedbackResponse(BaseModel):   # 형제 2 (응답용): 왼쪽 끝
    id: int
    child_id: int
    lesson_record_id: int
    next_goal: str
    teacher_feedback: str
    parent_feedback: str
    created_at: datetime

    # 강사가 수정한 본문(원본과 별도). edited가 아니면 None.
    edited_next_goal: Optional[str] = None
    edited_teacher_feedback: Optional[str] = None
    edited_parent_feedback: Optional[str] = None

    # Human Review 결과도 응답에 같이 보여준다
    review_status: str
    review_comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    class Config:                    # FeedbackResponse의 자식 (안쪽 4칸)
        from_attributes = True   # "딕셔너리만 읽는 지원에게 상자를 꺼내서 읽어도돼" 라고 권한을 주는것

