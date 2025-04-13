from pydantic import BaseModel, model_validator, ValidationError
from typing import List
from .options import OptionCreate
from datetime import datetime

class QuestionBase(BaseModel):
    text: str
    subject_id: int

class QuestionCreate(QuestionBase):
    options: List[OptionCreate]

    # enforce only four option for each question
    @model_validator(mode="before")
    def validate_options(cls, values):
        options = values.get("options")
        if len(options) != 4:
            raise ValueError("Exactly 4 options are required.")
        correct_count = sum(1 for opt in options if opt.is_correct)
        if correct_count != 1:
            raise ValueError("Exactly 1 option must be marked as correct.")
        return values
    
class QuestionOut(QuestionBase):
    id : int
    added_by : str
    added_on : datetime

    class Config:
        from_attributes = True
