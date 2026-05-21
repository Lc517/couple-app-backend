"""导入课程表数据到数据库"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, Base
from app.models.schedule import Schedule


def import_schedule():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "schedule.json")
    with open(data_path, "r", encoding="utf-8") as f:
        courses = json.load(f)

    # 清空已有数据
    db.query(Schedule).delete()

    for c in courses:
        schedule = Schedule(
            day_of_week=c["day_of_week"],
            period=c["period"],
            course_name=c["course_name"],
            classroom=c.get("classroom", ""),
            teacher=c.get("teacher", ""),
            weeks=c.get("weeks", ""),
        )
        db.add(schedule)

    db.commit()
    print(f"成功导入 {len(courses)} 条课程记录")
    db.close()


if __name__ == "__main__":
    import_schedule()
