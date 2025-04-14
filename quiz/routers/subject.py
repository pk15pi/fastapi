from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import subject as subject_schema
from models import subject as subject_model
import database
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional


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


# Get subject by ID
@router.get("/{subject_id}", response_model=subject_schema.SubjectOut)
def get_subject_by_id(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(subject_model.Subject).filter(subject_model.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

# Get subject by query parameter (e.g., name or code)
@router.get("/", response_model=List[subject_schema.SubjectOut])
def get_subjects(name: Optional[str] = Query(None), code: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(subject_model)
    if name:
        query = query.filter(subject_model.Subject.name.ilike(f"%{name}%"))
    if code:
        query = query.filter(subject_model.Subject.code.ilike(f"%{code}%"))
    return query.all()


# Update subject by ID
@router.put("/{subject_id}", response_model=subject_schema.SubjectOut)
def update_subject(subject_id: int, subject_data: subject_schema.Subjectupdate, db: Session = Depends(get_db)):
    subject = db.query(subject_model.Subject).filter(subject_model.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    for key, value in subject_data.dict(exclude_unset=True).items():
        setattr(subject, key, value)
    
    db.commit()
    db.refresh(subject)
    return subject

# Delete subject by ID
@router.delete("/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(subject_model.Subject).filter(subject_model.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(subject)
    db.commit()
    return {"message": "Subject deleted successfully"}
