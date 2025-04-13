from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import options as option_schema
from models import options as option_model
import database

router = APIRouter(prefix="/options", tags=["Options"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=option_schema.OptionOut)
def create_option(option: option_schema.OptionCreate, db: Session = Depends(get_db)):
    db_option = option_model.Option(**option.dict())
    db.add(db_option)
    db.commit()
    db.refresh(db_option)
    return db_option

@router.get("/", response_model=list[option_schema.OptionOut])
def read_options(db: Session = Depends(get_db)):
    return db.query(option_model.Option).all()
