from pydantic import BaseModel


class ChildCreate(BaseModel):
    name: str
    age: int
    gender: str | None = None
    level: str | None = None
    memo: str | None = None


class ChildResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str | None = None
    level: str | None = None
    memo: str | None = None

    class Config:
        from_attributes = True
        
#ChildCreate = 사용자가 POST로 보내는 데이터
#ChildResponse = 서버가 응답으로 돌려주는 데이터
