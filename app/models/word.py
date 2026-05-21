from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), nullable=False)
    meaning = Column(Text, nullable=False)
    phonetic = Column(String(100))
    example = Column(Text)
    level = Column(String(10), nullable=False)  # cet4 / cet6


class WordProgress(Base):
    __tablename__ = "word_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    familiarity = Column(Integer, default=0)
    last_review = Column(DateTime, server_default=func.now())
    next_review = Column(DateTime, server_default=func.now())
