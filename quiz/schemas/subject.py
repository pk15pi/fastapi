from pydantic import BaseModel

class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    pass

class Subjectupdate(SubjectBase):
    name : str

class SubjectOut(SubjectBase):
    id: int
    class Config:
        from_attributes = True