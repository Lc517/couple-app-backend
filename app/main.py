import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base, SessionLocal
from app.routers import auth, vocabulary, checkin, weather, period, schedule
from app.models import User, Word, WordProgress, DailyCheckin, Period, Schedule


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 创建数据库表
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Failed to create tables: {e}")
        traceback.print_exc()
    yield


app = FastAPI(title="Couple App API", version="1.0.0", lifespan=lifespan)

# CORS - 允许 Android 应用访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(vocabulary.router)
app.include_router(checkin.router)
app.include_router(weather.router)
app.include_router(period.router)
app.include_router(schedule.router)


@app.get("/")
def root():
    return {"message": "Couple App API is running!", "docs": "/docs"}


@app.get("/debug")
def debug():
    """测试数据库连接"""
    try:
        db = SessionLocal()
        result = db.execute(db.query(User).statement).fetchall()
        db.close()
        return {"status": "ok", "user_count": len(result)}
    except Exception as e:
        return {"status": "error", "error": str(e), "trace": traceback.format_exc()}
