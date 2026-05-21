from datetime import date, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.period import Period
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/period", tags=["period"])


class PeriodRequest(BaseModel):
    start_date: date
    end_date: date | None = None
    cycle_length: int | None = 28


@router.post("")
def record_period(req: PeriodRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    period = Period(
        user_id=user.id,
        start_date=req.start_date,
        end_date=req.end_date,
        cycle_length=req.cycle_length,
    )
    db.add(period)
    db.commit()
    return {"ok": True, "id": period.id}


@router.get("/predict")
def predict_period(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    records = db.query(Period).filter(
        Period.user_id == user.id,
    ).order_by(Period.start_date.desc()).all()

    if not records:
        return {"has_records": False}

    # 计算平均周期
    if len(records) >= 2:
        total_days = 0
        for i in range(len(records) - 1):
            delta = (records[i].start_date - records[i + 1].start_date).days
            total_days += delta
        avg_cycle = total_days / (len(records) - 1)
    else:
        avg_cycle = records[0].cycle_length or 28

    last_start = records[0].start_date
    next_start = last_start + timedelta(days=int(avg_cycle))
    today = date.today()
    days_until = (next_start - today).days

    # 预测安全期和易孕期
    safe_before = next_start - timedelta(days=8)
    safe_after = next_start + timedelta(days=8)
    fertile_start = next_start - timedelta(days=14)
    fertile_end = fertile_start + timedelta(days=6)

    return {
        "has_records": True,
        "last_start": str(last_start),
        "avg_cycle": int(avg_cycle),
        "next_start": str(next_start),
        "days_until": days_until,
        "safe_period_before": f"{safe_before} ~ {next_start - timedelta(days=1)}",
        "safe_period_after": f"{next_start + timedelta(days=1)} ~ {safe_after}",
        "fertile_period": f"{fertile_start} ~ {fertile_end}",
        "records": [{"start_date": str(r.start_date), "end_date": str(r.end_date) if r.end_date else None} for r in records],
    }
