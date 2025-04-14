from pydantic import BaseModel
from typing import Optional, List
from pydantic import BaseModel, EmailStr

# class UserCreate(BaseModel):
#     username: str
#     password: str

# class UserOut(BaseModel):
#     id: int
#     username: str
#     is_active: bool
#     class Config:
#         from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


# ---------- Shared Base ----------
class UserBase(BaseModel):
    username: str
    is_active: Optional[bool] = True
    contact: Optional[int] = None
    alternateContact: Optional[int] = None
    email: Optional[EmailStr] = ""
    city: Optional[str] = ""


# ---------- Read Schemas ----------
class UserOut(UserBase):
    id: int
    class Config:
        orm_mode = True


class UserGetById(UserOut):
    pass


# ---------- Create Schema ----------
class UserCreate(UserBase):
    hashed_password: str


# ---------- Full Update (PUT) ----------
class UserPut(UserCreate):
    pass


# ---------- Partial Update (PATCH) ----------
class UserUpdate(BaseModel):
    username: Optional[str] = None
    hashed_password: Optional[str] = None
    is_active: Optional[bool] = None
    contact: Optional[int] = None
    alternateContact: Optional[int] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None


# ---------- Bulk ----------
class BulkCreateUser(BaseModel):
    users: List[UserCreate]


class BulkUpdateUser(BaseModel):
    users: List[UserUpdate]


class BulkDeleteUser(BaseModel):
    user_ids: List[int]

