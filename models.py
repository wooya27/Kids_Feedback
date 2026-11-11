from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    level = Column(String(50), nullable=True)
    memo = Column(Text, nullable=True)
    #Day4에서 LLM 프롬프트에 아이 특징을 넣으려면 더 자세한 정보가 필요해.
    memory_hint = Column(Text, nullable=True)
    personality = Column(Text, nullable=True)
    preferred_feedback = Column(Text, nullable=True)
    caution_note = Column(Text, nullable=True)
    material_note = Column(Text, nullable=True)
    teacher_memo = Column(Text, nullable=True)
    lesson_records = relationship("LessonRecord", back_populates="child")



class LessonRecord(Base):
    __tablename__ = "lesson_records"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)

    lesson_date = Column(Date, nullable=False)
    activity = Column(Text, nullable=True)
    performance = Column(Text, nullable=True)
    attitude = Column(Text, nullable=True)
    difficulty = Column(Text, nullable=True)
    teacher_note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    child = relationship("Child", back_populates="lesson_records")


class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    lesson_record_id = Column(Integer, ForeignKey("lesson_records.id"), nullable=False)

    # ── AI 원본 초안 (절대 덮어쓰지 않고 보존) ──
    next_goal = Column(Text, nullable=True)
    teacher_feedback = Column(Text, nullable=True)
    parent_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ── 강사가 수정한 본문 (edited 상태일 때 채워짐, 원본과 별도 보관) ──
    # 원본(next_goal 등)은 그대로 두고, 수정본은 여기에 저장한다.
    # 최종본(final) = approved면 원본, edited면 수정본, rejected면 없음.
    edited_next_goal = Column(Text, nullable=True)
    edited_teacher_feedback = Column(Text, nullable=True)
    edited_parent_feedback = Column(Text, nullable=True)

    # ── Human Review (사람 검수 결과) ──
    # AI가 만든 초안을 강사가 보고 내린 판단을 여기에 남긴다.
    # pending(검수 전) → approved(그대로 승인) / edited(수정 후 사용) / rejected(폐기)
    # 이 값들이 쌓이면 승인률·수정률 같은 '수치'를 계산할 수 있다.
    review_status = Column(String(20), nullable=False, server_default="pending")
    review_comment = Column(Text, nullable=True)      # 강사가 남긴 코멘트(예: "보호자용 문장 더 쉽게")
    reviewed_at = Column(DateTime(timezone=True), nullable=True)  # 검수한 시각