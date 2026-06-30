from fastapi import FastAPI

from database import engine, Base
from models import Child, LessonRecord, Feedback
from routers.children_router import router as children_router
from routers.lesson_records_router import router as lesson_records_router
from routers.feedbacks_router import router as feedbacks_router
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(children_router)
app.include_router(lesson_records_router)
app.include_router(feedbacks_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Kids Feedback API is running"}

