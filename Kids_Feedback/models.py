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