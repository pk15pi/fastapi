from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import question as question_schema
from models import question as question_model
from models import options as option_model
import database

router = APIRouter(prefix="/questions", tags=["Questions"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=question_schema.QuestionOut)
def create_question(question: question_schema.QuestionCreate, db: Session = Depends(get_db)):
    db_question = question_model.Question(text=question.text, subject_id=question.subject_id)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for option in question.options:
        db_option = option_model.Option(
            text=option.text,
            is_correct=option.is_correct,
            question_id=db_question.id
        )
        db.add(db_option)
    db.commit()
    db.refresh(db_question)
    return db_question

@router.get("/", response_model=list[question_schema.QuestionOut])
def read_questions(db: Session = Depends(get_db)):
    return db.query(question_model.Question).all()
