from sqlalchemy.orm import Session
from .user import User

def create_user(db: Session, tg_id: int, name: str, phone: str, city: str, code: str = None, username: str = None):
    new_user = User(
        tg_id=tg_id,
        name=name,
        phone=phone,
        city=city,
        code=code,
        username=username
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_users(db: Session):
    return db.query(User).all()
