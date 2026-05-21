from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.word import Word, WordProgress
from app.models.checkin import DailyCheckin
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/vocabulary", tags=["vocabulary"])

# 间隔重复天数映射
REVIEW_INTERVALS = {
    0: 1,    # 新词，1天后复习
    1: 1,    # 1天后复习
    2: 3,    # 3天后复习
    3: 7,    # 7天后复习
    4: 14,   # 14天后复习
    5: 30,   # 30天后复习 (已掌握)
}


class ReviewRequest(BaseModel):
    word_id: int
    known: bool  # True = 认识, False = 不认识


class WordResponse(BaseModel):
    id: int
    word: str
    meaning: str
    phonetic: str | None
    example: str | None
    familiarity: int

    class Config:
        from_attributes = True


@router.get("/daily", response_model=list[WordResponse])
def get_daily_words(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.now()
    today = now.date()

    # 1. 查找需要复习的单词 (next_review <= now)
    review_words = (
        db.query(WordProgress, Word)
        .join(Word, WordProgress.word_id == Word.id)
        .filter(
            WordProgress.user_id == user.id,
            WordProgress.next_review <= now,
        )
        .all()
    )

    result = []
    for progress, word in review_words:
        result.append(WordResponse(
            id=word.id, word=word.word, meaning=word.meaning,
            phonetic=word.phonetic, example=word.example,
            familiarity=progress.familiarity,
        ))

    # 2. 如果复习单词不够，补充新词
    needed = user.daily_word_goal - len(result)
    if needed > 0:
        # 已学过的单词ID
        learned_ids = [wp.word_id for wp in db.query(WordProgress.word_id)
                       .filter(WordProgress.user_id == user.id).all()]
        # 按 exam_level 筛选新词
        query = db.query(Word).filter(Word.level == user.exam_level)
        if learned_ids:
            query = query.filter(~Word.id.in_(learned_ids))
        new_words = query.order_by(func.random()).limit(needed).all()

        for word in new_words:
            result.append(WordResponse(
                id=word.id, word=word.word, meaning=word.meaning,
                phonetic=word.phonetic, example=word.example,
                familiarity=0,
            ))

    return result


@router.put("/review")
def review_word(req: ReviewRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.now()

    progress = db.query(WordProgress).filter(
        WordProgress.user_id == user.id,
        WordProgress.word_id == req.word_id,
    ).first()

    if req.known:
        if progress:
            new_familiarity = min(progress.familiarity + 1, 5)
            progress.familiarity = new_familiarity
            progress.last_review = now
            progress.next_review = now + timedelta(days=REVIEW_INTERVALS[new_familiarity])
        else:
            progress = WordProgress(
                user_id=user.id,
                word_id=req.word_id,
                familiarity=1,
                last_review=now,
                next_review=now + timedelta(days=REVIEW_INTERVALS[1]),
            )
            db.add(progress)
    else:
        if progress:
            progress.familiarity = 0
            progress.last_review = now
            progress.next_review = now + timedelta(days=REVIEW_INTERVALS[0])
        else:
            progress = WordProgress(
                user_id=user.id,
                word_id=req.word_id,
                familiarity=0,
                last_review=now,
                next_review=now + timedelta(days=REVIEW_INTERVALS[0]),
            )
            db.add(progress)

    db.commit()
    return {"ok": True, "familiarity": progress.familiarity}


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    today = date.today()
    total_words = db.query(func.count(Word.id)).filter(Word.level == user.exam_level).scalar()
    learned = db.query(func.count(WordProgress.id)).filter(WordProgress.user_id == user.id).scalar()
    mastered = db.query(func.count(WordProgress.id)).filter(
        WordProgress.user_id == user.id,
        WordProgress.familiarity >= 5,
    ).scalar()
    today_learned = db.query(func.count(WordProgress.id)).filter(
        WordProgress.user_id == user.id,
        func.date(WordProgress.last_review) == today,
    ).scalar()

    return {
        "total_words": total_words,
        "learned": learned,
        "mastered": mastered,
        "today_learned": today_learned,
        "daily_goal": user.daily_word_goal,
    }


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
