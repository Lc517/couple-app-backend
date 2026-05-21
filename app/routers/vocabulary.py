from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.checkin import DailyCheckin
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/vocabulary", tags=["vocabulary"])


@router.get("/partner-status")
def get_partner_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user.partner_id:
        return {"has_partner": False}

    partner = db.query(User).filter(User.id == user.partner_id).first()
    if not partner:
        return {"has_partner": False}

    today = date.today()
    partner_today = db.query(DailyCheckin).filter(
        DailyCheckin.user_id == partner.id,
        DailyCheckin.date == today,
    ).first()

    return {
        "has_partner": True,
        "partner_nickname": partner.nickname,
        "partner_checked_in": partner_today is not None,
        "partner_words_learned": partner_today.words_learned if partner_today else 0,
    }
