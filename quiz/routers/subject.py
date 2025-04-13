from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import subject as subject_schema
from models import subject as subject_model
import database

router = APIRouter(prefix="/subjects", tags=["Subjects"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=subject_schema.SubjectOut)
def create_subject(subject: subject_schema.SubjectCreate, db: Session = Depends(get_db)):
    # Creating the Subject instance using the input data
    db_subject = subject_model.Subject(**subject.dict())
    
    # Adding and committing the new subject to the DB
    db.add(db_subject)
    db.commit()
    
    # Refreshing to get the latest state from DB (including auto-generated fields like id)
    db.refresh(db_subject)
    
    return db_subject

@router.get("/", response_model=list[subject_schema.SubjectOut])
def read_subjects(db: Session = Depends(get_db)):
    # Querying all subjects and returning the list
    return db.query(subject_model.Subject).all()
