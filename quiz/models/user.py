from pydantic import EmailStr
from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    contact = Column(Integer, default=None)
    alternateContact = Column(Integer, default=None)
    email = Column(EmailStr, default='')
    city = Column(String, default='')

