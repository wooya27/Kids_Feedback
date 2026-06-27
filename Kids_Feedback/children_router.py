from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Child
from schemas import ChildCreate, ChildResponse

router = APIRouter(
    prefix="/children",
    tags=["children"]
)


@router.post("/", response_model=ChildResponse)
def create_child(child: ChildCreate, db: Session = Depends(get_db)):
    new_child = Child(
        name=child.name,
        age=child.age,
        gender=child.gender,
        level=child.level,
        memo=child.memo
    )
# post 저장부분
    db.add(new_child)
    db.commit()
    db.refresh(new_child)

    return new_child


@router.get("/", response_model=list[ChildResponse])
def get_children(db: Session = Depends(get_db)):
    children = db.query(Child).all() #조회 부분
    return children


@router.get("/{child_id}", response_model=ChildResponse)
def get_child(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    return child