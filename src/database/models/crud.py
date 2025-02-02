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

def add_user_telegram(db: Session, user_id: int, tg_id: int, username: str = None):
    user = db.query(User).filter(User.id == user_id).first()
    user.telegram_users.append(TelegramUser(telegram=tg_id, username=username))
    db.commit()
    db.refresh(user)
    return user

def get_users(db: Session) -> list[User]:
    return db.query(User).all()
