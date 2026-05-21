from sqlalchemy import Column, Integer, Date, ForeignKey
from app.database import Base


class DailyCheckin(Base):
    __tablename__ = "daily_checkin"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    words_learned = Column(Integer, default=0)
    words_reviewed = Column(Integer, default=0)
    streak = Column(Integer, default=0)
