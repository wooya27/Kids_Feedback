import logging

from fastapi import FastAPI

# ── 로그 기본 설정: 시간 + 레벨 + 메시지 형태로 콘솔에 찍기 ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

from sqlalchemy import text

from database import engine, Base
from models import Child, LessonRecord, Feedback
from routers.children_router import router as children_router
from routers.lesson_records_router import router as lesson_records_router
from routers.feedbacks_router import router as feedbacks_router

# create_all은 '없는 테이블'만 새로 만든다. 이미 존재하는 feedbacks 테이블에는
# 새로 추가한 Human Review 컬럼이 자동으로 안 생긴다(이게 흔한 함정).
# 그래서 ADD COLUMN IF NOT EXISTS로 '있으면 말고 없으면 추가' 한 번 보정한다. (가벼운 수동 마이그레이션)
Base.metadata.create_all(bind=engine)

def _ensure_review_columns():
    stmts = [
        "ALTER TABLE feedbacks ADD COLUMN IF NOT EXISTS review_status VARCHAR(20) NOT NULL DEFAULT 'pending'",
        "ALTER TABLE feedbacks ADD COLUMN IF NOT EXISTS review_comment TEXT",
        "ALTER TABLE feedbacks ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ",
        # P1-3: 강사 수정 본문(원본과 별도 보관)
        "ALTER TABLE feedbacks ADD COLUMN IF NOT EXISTS edited_next_goal TEXT",
        "ALTER TABLE feedbacks ADD COLUMN IF NOT EXISTS edited_teacher_feedback TEXT",
        "ALTER TABLE feedbacks ADD COLUMN IF NOT EXISTS edited_parent_feedback TEXT",
    ]
    with engine.begin() as conn:  # begin() = 자동 커밋되는 트랜잭션
        for s in stmts:
            conn.execute(text(s))

_ensure_review_columns()

app = FastAPI() #main.py 안의 app = FastAPI()라는 코드가 실행되면서 FastAPI 앱 객체가 만들어지는 것

app.include_router(children_router)
app.include_router(lesson_records_router)
app.include_router(feedbacks_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Kids Feedback API is running"}

