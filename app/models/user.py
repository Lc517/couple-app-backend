from sqlalchemy import Column, Integer, String, Time, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    nickname = Column(String(50))
    role = Column(String(10))  # boyfriend / girlfriend
    password_hash = Column(String(255), nullable=False)
    exam_level = Column(String(10), nullable=False)  # cet4 / cet6
    daily_word_goal = Column(Integer, default=50)
    morning_reminder = Column(Time, default=None)
    evening_reminder = Column(Time, default=None)
    partner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
