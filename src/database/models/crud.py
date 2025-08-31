from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.database.models.support_req import SupportRequest
from .user import TelegramUser, User
from .session import TgSession
from .request import SendRequest, DeliveryRequest


def create_session(db: Session, user_id: int) -> TgSession: 
    new_session = TgSession(user_id=user_id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def delete_session(db: Session, user_id: int):
    session = db.query(TgSession).filter(TgSession.user_id == user_id).first()
    db.delete(session)
    db.commit()

def get_session_by_tg_id(db: Session, tg_id: str) -> Optional[TgSession]:
    tg_user = db.query(TelegramUser).filter(TelegramUser.telegram == str(tg_id)).first()
    if not tg_user:
        return None
    session = db.query(TgSession).filter(TgSession.user_id == tg_user.user_id).first()
    return session

def set_user_id_for_tg_user(db: Session, tg_id: int, user_id: int):
    tg_user = db.query(TelegramUser).filter(TelegramUser.telegram == tg_id).first()
    tg_user.user_id = user_id
    db.commit()
    

def create_user(db: Session, phone: str, name: str, city: str) -> User:
    new_user = User(
        phone=phone,
        name=name,
        city=city,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def is_user_phone_exists(db: Session, phone: int) -> bool:
    return db.query(User).filter(User.phone == phone).count() > 0

def get_user_by_phone(db: Session, phone: int) -> User:
    return db.query(User).filter(User.phone == phone).first()

def get_user_by_id(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()

def add_user_telegram(db: Session, user_id: int, tg_id: int, username: str = None):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    telegram_user = TelegramUser(user_id=user.id, telegram=tg_id, username=username)
    db.add(telegram_user)
    db.commit()
    db.refresh(telegram_user)
    
    return user

def delete_user_telegram(db: Session, tg_id: int):
    tg_user = db.query(TelegramUser).filter(TelegramUser.telegram == tg_id).first()
    db.delete(tg_user)
    db.commit()

def get_users(db: Session) -> list[User]:
    return db.query(User).all()

def is_tg_user_exists(db: Session, tg_id: int) -> bool:
    return db.query(TelegramUser).filter(TelegramUser.telegram == tg_id).count() > 0

def get_city_by_tg_id(db: Session, tg_id: int) -> str:
    return db.query(User).join(TelegramUser).filter(TelegramUser.telegram == tg_id).first().city

def get_user_by_tg_id(db: Session, tg_id: int) -> User:
    return db.query(User).join(TelegramUser).filter(TelegramUser.telegram == tg_id).first()

def add_tg_user(db, tg_id: int, username: str = None):
    new_tg_user = TelegramUser(telegram=tg_id, username=username)
    db.add(new_tg_user)
    db.commit()
    db.refresh(new_tg_user)

    return new_tg_user

def get_tg_user(db: Session, tg_id: int) -> TelegramUser:
    return db.query(TelegramUser).filter(TelegramUser.telegram == tg_id).first()

def accept_terms(db: Session, tg_id: int):
    tg_user = get_tg_user(db, tg_id)
    tg_user.accepted_terms = True
    db.commit()






def get_tg_user_by_tg_id(db: Session, tg_id: int):
    return db.query(TelegramUser).filter(TelegramUser.telegram == tg_id).first()
    

def create_supp_request(db: Session, tg_id: int, message: str, req_type = None) -> SupportRequest:
    user = get_user_by_tg_id(db, tg_id)
    tg_user = get_tg_user_by_tg_id(db, tg_id)
    
    if user:
        new_request = SupportRequest(
            user_id=user.id,    
            telegram_user=tg_user,
            req_type=req_type,
            message=message
        )
    else:
        new_request = SupportRequest(
            user_id=None,
            telegram_user=tg_user,
            req_type=req_type,
            message=message
        )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

def get_user_from_supp_req(db: Session, supp_req: SupportRequest) -> User:
    return supp_req.user

