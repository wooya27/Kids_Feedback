# seed.py — 데모용 샘플 데이터 넣기 (재현 가능한 E2E 테스트용)
# 실행(Docker db 대상): DATABASE_URL 환경변수로 localhost:5432를 가리켜서 실행
import datetime

from database import SessionLocal, engine, Base
from models import Child, LessonRecord

Base.metadata.create_all(bind=engine)   # 테이블 없으면 생성
db = SessionLocal()

if db.query(Child).count() == 0:
    child = Child(
        name="유리",
        age=8,
        gender="여",
        level="초급",
        memory_hint="분홍 줄넘기",
        personality="위축형(소심하고 실수를 두려워함)",
        preferred_feedback="작은 성공을 구체적으로 칭찬",
        caution_note="다른 아이와 비교 금지",
        material_note="줄넘기 길이 조정 필요",
        teacher_memo="발표를 어려워함",
    )
    db.add(child)
    db.flush()   # child.id 확보 (아직 commit 전)

    records = [
        LessonRecord(
            child_id=child.id,
            lesson_date=datetime.date(2026, 11, 1),
            activity="양발 모아 뛰기",
            performance="10회 성공",
            attitude="소극적이지만 끝까지 함",
            teacher_note="처음으로 혼자 10회 성공",
        ),
        LessonRecord(
            child_id=child.id,
            lesson_date=datetime.date(2026, 11, 5),
            activity="한 발 번갈아 뛰기",
            performance="5회",
            attitude="집중함",
            teacher_note="균형 잡기 연습 필요",
        ),
    ]
    db.add_all(records)
    db.commit()
    print("seed 완료 - child_id:", child.id, "/ lesson_record ids:", [r.id for r in records])
else:
    print("이미 데이터 있음 → seed 건너뜀. children =", db.query(Child).count())

db.close()
