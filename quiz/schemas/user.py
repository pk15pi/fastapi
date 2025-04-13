from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
