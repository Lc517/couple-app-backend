from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schedule import Schedule
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

# 当前学期第1周的起始日期
SEMESTER_START = date(2026, 3, 2)

# 每节课的时间 (100分钟/节，课间休息20分钟)
PERIOD_TIMES = {
    1: {"start_time": "08:00", "end_time": "09:40"},
    2: {"start_time": "10:00", "end_time": "11:40"},
    3: {"start_time": "14:30", "end_time": "16:10"},
    4: {"start_time": "16:30", "end_time": "18:10"},
    5: {"start_time": "19:00", "end_time": "20:40"},
}


def get_current_week() -> int:
    today = date.today()
    delta = (today - SEMESTER_START).days
    return max(1, delta // 7 + 1)


def parse_weeks(weeks_str: str) -> list[int]:
    """解析周次字符串，如 '2-13' -> [2,3,4,...,13], '4,6,8' -> [4,6,8]"""
    result = []
    for part in weeks_str.split(","):
        if "-" in part:
            start, end = part.split("-")
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(part))
    return result


@router.get("/today")
def get_today_schedule(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    today = date.today()
    day_of_week = today.isoweekday()  # 1=Monday, 7=Sunday
    current_week = get_current_week()

    if day_of_week > 5:  # 周六日无课
        return {"day": day_of_week, "week": current_week, "courses": []}

    courses = db.query(Schedule).filter(Schedule.day_of_week == day_of_week).all()

    result = []
    for c in courses:
        weeks = parse_weeks(c.weeks) if c.weeks else []
        if current_week in weeks or not c.weeks:
            times = PERIOD_TIMES.get(c.period, {})
            result.append({
                "id": c.id,
                "period": c.period,
                "course_name": c.course_name,
                "classroom": c.classroom,
                "teacher": c.teacher,
                "start_time": times.get("start_time", ""),
                "end_time": times.get("end_time", ""),
            })

    result.sort(key=lambda x: x["period"])
    return {"day": day_of_week, "week": current_week, "courses": result}


@router.get("/{day}")
def get_schedule_by_day(day: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if day < 1 or day > 7:
        return {"day": day, "week": get_current_week(), "courses": []}

    current_week = get_current_week()
    courses = db.query(Schedule).filter(Schedule.day_of_week == day).all()

    result = []
    for c in courses:
        weeks = parse_weeks(c.weeks) if c.weeks else []
        if current_week in weeks or not c.weeks:
            times = PERIOD_TIMES.get(c.period, {})
            result.append({
                "id": c.id,
                "period": c.period,
                "course_name": c.course_name,
                "classroom": c.classroom,
                "teacher": c.teacher,
                "weeks": c.weeks,
                "start_time": times.get("start_time", ""),
                "end_time": times.get("end_time", ""),
            })

    result.sort(key=lambda x: x["period"])
    return {"day": day, "week": get_current_week(), "courses": result}
