## 데이터를 받아 실제로 처리하는곳

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Child
from schemas import ChildCreate, ChildResponse,ChildUpdate


router = APIRouter(
    prefix="/children",
    tags=["children"]
)


@router.post("/", response_model=ChildResponse) #생성
def create_child(child: ChildCreate, db: Session = Depends(get_db)):
    new_child = Child(
        name=child.name,
        age=child.age,
        gender=child.gender,
        level=child.level,
        memo=child.memo,
        memory_hint=child.memory_hint,
        personality=child.personality,
        preferred_feedback=child.preferred_feedback,
        caution_note=child.caution_note,
        material_note=child.material_note,
        teacher_memo=child.teacher_memo
        #왼쪽: DB 컬럼 이름 (models.py에 정의된 것) ,오른쪽: 사용자가 보낸 데이터 (schemas.py에서 받은 것)
    )
# post 저장부분 
    db.add(new_child)
    db.commit()
    db.refresh(new_child)

    return new_child


@router.get("/", response_model=list[ChildResponse]) #조회
def get_children(db: Session = Depends(get_db)):
    children = db.query(Child).all() #전체 조회 부분
    return children


@router.get("/{child_id}", response_model=ChildResponse)
def get_child(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    return child


@router.patch("/{child_id}")
def update_child(child_id: int, child: ChildUpdate, db: Session = Depends(get_db)):
    db_child = db.query(Child).filter(Child.id == child_id).first()
    update_data = child.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_child,key,value)
    
    db.commit()
    db.refresh(db_child)
    return db_child