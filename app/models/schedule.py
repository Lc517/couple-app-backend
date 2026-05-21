from sqlalchemy import Column, Integer, String
from app.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer, nullable=False)  # 1-5
    period = Column(Integer, nullable=False)  # 1-5
    course_name = Column(String(100), nullable=False)
    classroom = Column(String(100))
    teacher = Column(String(50))
    weeks = Column(String(50))
