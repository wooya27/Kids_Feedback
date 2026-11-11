# tests/conftest.py
# 테스트 공통 준비물(픽스처)을 모아두는 파일. pytest가 자동으로 읽는다.
#
# 핵심 아이디어 2가지:
#   1) 진짜 PostgreSQL 대신 메모리 SQLite를 쓴다 → DB 서버 없이도 테스트가 돈다.
#   2) 진짜 Gemini(LLM/임베딩) 대신 가짜 함수(Mock)로 바꿔치기 → API 키·네트워크 없이 돈다.
#
# 그래서 이 테스트들은 "DB에 저장됐나/안 됐나", "실패를 제대로 걸러내나" 같은
# '우리 코드의 로직'만 검증한다. (외부 LLM 품질은 여기서 검증하지 않는다 = P1-4 방침)

import os

# genai.Client(api_key=...) 생성 시 빈 키로 터지지 않도록 더미 키를 먼저 넣는다.
# (.env에 실제 키가 있으면 python-dotenv는 기존 env를 덮어쓰지 않으므로 그대로 둠)
os.environ.setdefault("GEMINI_API_KEY", "test-dummy-key")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date

from database import Base, get_db
import models
from models import Child, LessonRecord
from routers.feedbacks_router import router as feedbacks_router


# ── 메모리 SQLite 엔진 (테스트 한 세션 동안 유지) ──
# StaticPool + 단일 연결: 메모리 DB가 연결마다 초기화되지 않도록 묶어준다.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db_session():
    """매 테스트마다 테이블을 새로 만들고, 끝나면 비운다(격리)."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def seeded_child(db_session):
    """아이 1명 + 수업기록 1건을 심고 lesson_record_id를 돌려준다."""
    child = Child(name="테스트아이", age=8, personality="위축형(소심함)",
                  preferred_feedback="구체적 칭찬")
    db_session.add(child)
    db_session.flush()
    rec = LessonRecord(child_id=child.id, lesson_date=date(2026, 11, 1),
                       activity="양발 모아 뛰기", attitude="머뭇거림",
                       teacher_note="1회차")
    db_session.add(rec)
    db_session.commit()
    return rec.id


@pytest.fixture()
def app(db_session):
    """테스트용 FastAPI 앱: feedbacks 라우터만 올리고 get_db를 SQLite로 교체.
    (api.main은 Postgres 전용 마이그레이션을 실행하므로 테스트에서 import하지 않는다)
    """
    test_app = FastAPI()
    test_app.include_router(feedbacks_router)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture()
def client(app):
    return TestClient(app)
