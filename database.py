import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# ── DB 주소: 환경변수(DATABASE_URL)가 있으면 그걸, 없으면 로컬 기본값 ──
#  Docker에선 compose가 DATABASE_URL을 넣어줌 (host가 localhost가 아니라 'db' 서비스).
#  내 PC에서 그냥 돌릴 땐 env가 없으니 아래 기본값(localhost)을 쓴다.
DATABASE_URL = os.getenv("DATABASE_URL") or URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="1234",
    host="localhost",
    port=5432,
    database="kids_feedback_db",
)

engine = create_engine(DATABASE_URL) # DB랑 연결하는 엔진

SessionLocal = sessionmaker(      
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base() # 모든 모델(테이블)의 부모. models.py가 이걸 상속함


def get_db():
    db = SessionLocal() # 문열기
    try:
        yield db #라우터한테 빌려줌
    finally:
        db.close() #끝나면 묻 닫기

        