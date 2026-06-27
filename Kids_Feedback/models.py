from sqlalchemy import Column, Integer, String
from database import Base


class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=True)
    level = Column(String, nullable=True)
    memo = Column(String, nullable=True)