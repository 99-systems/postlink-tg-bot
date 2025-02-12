from sqlalchemy.orm import Session
from .user import TelegramUser, User

def create_user(db: Session, tg_id: int, name: str, phone: str, city: str, code: str = None, username: str = None) -> User:
    new_user = User(
        name=name,
        phone=phone,
        city=city,
        code=code,
        
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_tg_user = TelegramUser(
        telegram=tg_id,
        user_id=new_user.id,
        username=username
    )
    db.add(new_tg_user)
    db.commit()

    return new_user

def is_user_phone_exists(db: Session, phone: int) -> bool:
    return db.query(User).filter(User.phone == phone).count() > 0

def get_user_by_phone(db: Session, phone: int) -> User:
    return db.query(User).filter(User.phone == phone).first()

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