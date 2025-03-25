from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.database.models.support_req import SupportRequest
from .user import TelegramUser, User
from .request import SendRequest, DeliveryRequest
from .session import TgSession


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

def get_session_by_tg_id(db: Session, tg_id: int) -> Optional[TgSession]:
    tg_user = db.query(TelegramUser).filter(TelegramUser.telegram == tg_id).first()
    if not tg_user:
        return None
    return db.query(TgSession).filter(TgSession.user_id == tg_user.user_id).first()

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


def create_send_request(db: Session, tg_id: int, from_location: str, to_location: str, from_date: str, to_date: str, size_type: str, description: str = None) -> SendRequest:
    from_date = datetime.strptime(from_date.strip(), "%d.%m.%Y")
    to_date = datetime.strptime(to_date.strip(), "%d.%m.%Y")
    
    new_request = SendRequest(
        from_location=from_location,
        to_location=to_location,
        user_id=get_user_by_tg_id(db, tg_id).id,
        from_date=from_date,
        to_date=to_date,
        size_type=size_type,
        description=description
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request

def create_delivery_request(db: Session, tg_id: int, from_location: str, to_location: str, from_date: str | datetime, to_date: str | datetime, size_type: str) -> Optional[DeliveryRequest]:

    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date.strip(), "%d.%m.%Y")
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date.strip(), "%d.%m.%Y")

    user = get_user_by_tg_id(db, tg_id)
    if not user:
        return None

    new_request = DeliveryRequest(
        from_location=from_location,
        to_location=to_location,
        user_id=user.id,
        from_date=from_date,
        to_date=to_date,
        size_type=size_type
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

def get_matched_requests_for_send(db: Session, send_req: SendRequest) -> list[DeliveryRequest]:
    return db.query(DeliveryRequest).filter(
        DeliveryRequest.from_location == send_req.from_location,
        or_(DeliveryRequest.to_location == send_req.to_location, DeliveryRequest.to_location == '*'),
        and_(
            DeliveryRequest.from_date <= send_req.to_date,
            DeliveryRequest.to_date >= send_req.from_date
        ),
        or_(
            DeliveryRequest.size_type == send_req.size_type, 
            DeliveryRequest.size_type == 'Не указаны', 
            send_req.size_type == 'Не указаны'
        ),
        DeliveryRequest.status == 'open'
    ).all()

def get_matched_requests_for_delivery(db: Session, delivery_req: DeliveryRequest) -> list[SendRequest]:
    return db.query(SendRequest).filter(
        SendRequest.from_location == delivery_req.from_location,
        or_(SendRequest.to_location == delivery_req.to_location, delivery_req.to_location == '*'),
        and_(
            SendRequest.from_date <= delivery_req.to_date,
            SendRequest.to_date >= delivery_req.from_date
        ),
        or_(
            SendRequest.size_type == delivery_req.size_type, 
            SendRequest.size_type == 'Не указаны', 
            delivery_req.size_type == 'Не указаны'
        ),
        SendRequest.status == 'open'
    ).all()

def get_request_status_by_tg_id(db: Session, tg_id: int) -> Optional[str]:
    user = get_user_by_tg_id(db, tg_id)
    if not user:
        return None

    send_req = db.query(SendRequest).filter(SendRequest.user_id == user.id, SendRequest.status == 'open').first()
    delivery_req = db.query(DeliveryRequest).filter(DeliveryRequest.user_id == user.id, DeliveryRequest.status == 'open').first()

    if send_req:
        return 'send'
    elif delivery_req:
        return 'delivery'
    else:
        return None

    

def is_open_request_by_tg_id(db: Session, tg_id: int) -> bool:
    req_status = get_request_status_by_tg_id(db, tg_id)

    if req_status:
        return True
    return False
        
def get_request_by_tg_id(db: Session, tg_id: int) -> Optional[List[SendRequest | DeliveryRequest]]:
    user = get_user_by_tg_id(db, tg_id)
    
    requests = (
        db.query(DeliveryRequest)
        .filter(DeliveryRequest.user_id == user.id, DeliveryRequest.status == 'open')
        .all()
    )
    requests += (
        db.query(SendRequest)
        .filter(SendRequest.user_id == user.id, SendRequest.status == 'open')
        .all()
    )

    return requests

def close_send_request(db: Session, req_id: int):
    req = db.query(SendRequest).filter(SendRequest.id == req_id).first()
    req.status = 'closed'
    db.commit()

def close_delivery_request(db: Session, req_id: int):
    req = db.query(DeliveryRequest).filter(DeliveryRequest.id == req_id).first()
    req.status = 'closed'
    db.commit()

def get_tg_user_by_tg_id(db: Session, tg_id: int):
    return db.query(TelegramUser).filter(TelegramUser.telegram == tg_id).first()
    

def create_supp_request(db: Session, tg_id: int, message: str, req_type = None, req_id = None) -> SupportRequest:
    user = get_user_by_tg_id(db, tg_id)
    tg_user = get_tg_user_by_tg_id(db, tg_id)
    
    if user:
        new_request = SupportRequest(
            user_id=user.id,    
            telegram_user=tg_user,
            req_type=req_type,
            req_id=req_id,
            message=message
        )
    else:
        new_request = SupportRequest(
            user_id=None,
            telegram_user=tg_user,
            req_type=req_type,
            req_id=req_id,
            message=message
        )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

def get_user_from_supp_req(db: Session, supp_req: SupportRequest) -> User:
    return supp_req.user

def get_all_req_ids_by_user(db: Session, user: User) -> List[int]:
    send_req_ids = [req.id for req in user.send_requests]
    delivery_req_ids = [req.id for req in user.delivery_requests]

    return {'send': send_req_ids, 'delivery': delivery_req_ids}

def get_all_requests(db: Session):
    requests = db.query(SendRequest).all()
    requests += db.query(DeliveryRequest).all()
    return requests

def get_all_send_requests(db: Session):
    return db.query(SendRequest).all()

def get_all_delivery_requests(db: Session):
    return db.query(DeliveryRequest).all()

def get_send_request_by_id(db: Session, req_id: int):
    return db.query(SendRequest).filter(SendRequest.id == req_id).first()

def get_delivery_request_by_id(db: Session, req_id: int):
    return db.query(DeliveryRequest).filter(DeliveryRequest.id == req_id).first()