## 데이터를 받아 실제로 처리하는곳

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session 
from sqlalchemy import desc
from database import get_db
from models import LessonRecord
from schemas import LessonRecordCreate, LessonRecordResponse


router = APIRouter(
    prefix="/lesson",
    tags=["lesson"]
)


@router.post("/", response_model=LessonRecordResponse) #생성
def create_LessonRecord(record: LessonRecordCreate, db: Session = Depends(get_db)):
    new_LessonRecord = LessonRecord(
        child_id=record.child_id,
        lesson_date=record.lesson_date,
        activity=record.activity,
        performance=record.performance,
        attitude=record.attitude,
        difficulty=record.difficulty,
       teacher_note=record.teacher_note
        #왼쪽: DB 컬럼 이름 (models.py에 정의된 것) ,오른쪽: 사용자가 보낸 데이터 (schemas.py에서 받은 것)
    )


# post 저장부분 
    db.add(new_LessonRecord)
    db.commit()
    db.refresh(new_LessonRecord)

    return new_LessonRecord

#db.query(LessonRecord) 뒤에 메서드를 체이닝(이어붙이기) 하는 방식이야. 점(.)으로 계속 연결해.
@router.get("/", response_model=list[LessonRecordResponse]) #조회
def get_LessonRecordren(db: Session = Depends(get_db)):
    Children = db.query(LessonRecord).all() # 전체 조회 부분
    return Children



# .filter() — 조건으로 거르기 (어느 아이?) db.query(LessonRecord).filter(LessonRecord.child_id ==3).all()
  # child_id가 3인 기록만
  
@router.get("/{child_id}/leasson-records") #조회
def get_lesson_records(child_id: int, db: Session = Depends(get_db)):
    Children = db.query(LessonRecord).filter(LessonRecord.child_id == child_id).order_by(desc(LessonRecord.lesson_date)).limit(5).all() #조회 부분
    return Children



