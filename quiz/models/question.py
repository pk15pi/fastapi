from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"))

    subject = relationship("Subject", backref="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")

    added_on = Column(DateTime, default=datetime.utcnow)
    added_by = Column(String, default="Prasenjit")

