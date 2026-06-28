from fastapi import FastAPI

from database import engine, Base
from models import Child
from children_router import router as children_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(children_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Kids Feedback API is running"}