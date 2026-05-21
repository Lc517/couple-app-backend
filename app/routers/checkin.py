from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.checkin import DailyCheckin
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/checkin", tags=["checkin"])


@router.post("")
def do_checkin(words_learned: int = 0, words_reviewed: int = 0,
               db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    today = date.today()

    existing = db.query(DailyCheckin).filter(
        DailyCheckin.user_id == user.id,
        DailyCheckin.date == today,
    ).first()

    if existing:
        existing.words_learned = words_learned
        existing.words_reviewed = words_reviewed
        db.commit()
        return {"ok": True, "streak": existing.streak, "updated": True}

    # 计算连续天数
    yesterday = today - timedelta(days=1)
    yesterday_checkin = db.query(DailyCheckin).filter(
        DailyCheckin.user_id == user.id,
        DailyCheckin.date == yesterday,
    ).first()
    streak = (yesterday_checkin.streak + 1) if yesterday_checkin else 1

    checkin = DailyCheckin(
        user_id=user.id,
        date=today,
        words_learned=words_learned,
        words_reviewed=words_reviewed,
        streak=streak,
    )
    db.add(checkin)
    db.commit()
    return {"ok": True, "streak": streak, "updated": False}


@router.get("/stats")
def get_checkin_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    today = date.today()

    # 今日打卡状态
    today_checkin = db.query(DailyCheckin).filter(
        DailyCheckin.user_id == user.id,
        DailyCheckin.date == today,
    ).first()

    # 连续天数
    streak = today_checkin.streak if today_checkin else 0

    # 本月打卡数据 (日历用)
    first_day = today.replace(day=1)
    checkins = db.query(DailyCheckin).filter(
        DailyCheckin.user_id == user.id,
        DailyCheckin.date >= first_day,
        DailyCheckin.date <= today,
    ).all()

    calendar = {str(c.date): {"learned": c.words_learned, "reviewed": c.words_reviewed} for c in checkins}

    # 总打卡天数
    total_days = db.query(func.count(DailyCheckin.id)).filter(
        DailyCheckin.user_id == user.id,
    ).scalar()

    return {
        "today_checked_in": today_checkin is not None,
        "streak": streak,
        "total_days": total_days,
        "today_words_learned": today_checkin.words_learned if today_checkin else 0,
        "today_words_reviewed": today_checkin.words_reviewed if today_checkin else 0,
        "calendar": calendar,
    }
