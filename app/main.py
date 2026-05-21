from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.routers import auth, vocabulary, checkin, weather, period, schedule
from app.models import User, Word, WordProgress, DailyCheckin, Period, Schedule


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
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
