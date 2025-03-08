from sqlalchemy.orm import Session
from .user import TelegramUser, User
from .request import SendRequest, DeliveryRequest
from typing import List, Optional
from sqlalchemy import and_, or_

from datetime import datetime

def create_user(db: Session, tg_id: int, name: str, phone: str, city: str, code: str = None, username: str = None) -> User:
    new_user = User(
        name=name,
        phone=phone,
        city=city,
        code=code,
        telegram_user=TelegramUser(telegram=tg_id, username=username)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

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

def get_city_by_tg_id(db: Session, tg_id: int) -> str:
    return db.query(User).join(TelegramUser).filter(TelegramUser.telegram == tg_id).first().city

def get_user_by_tg_id(db: Session, tg_id: int) -> User:
    return db.query(User).join(TelegramUser).filter(TelegramUser.telegram == tg_id).first()


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

def create_delivery_request(db: Session, tg_id: int, from_location: str, to_location: str, delivery_date: str, size_type: str) -> DeliveryRequest:
    delivery_date = datetime.strptime(delivery_date.strip(), "%d.%m.%Y")
    new_request = DeliveryRequest(
        from_location=from_location,
        to_location=to_location,
        user_id=get_user_by_tg_id(db, tg_id).id,
        delivery_date=delivery_date,
        size_type=size_type
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request

def get_matched_requests_for_send(db: Session, send_req: SendRequest) -> list[DeliveryRequest]:
    return db.query(DeliveryRequest).filter(
        DeliveryRequest.from_location == send_req.from_location,
        DeliveryRequest.to_location == send_req.to_location,
        and_(send_req.from_date <= DeliveryRequest.delivery_date, 
             DeliveryRequest.delivery_date <= send_req.to_date),
        or_(DeliveryRequest.size_type == send_req.size_type, DeliveryRequest.size_type == 'Не указаны'),
        DeliveryRequest.status == 'open'
    ).all()

def get_matched_requests_for_delivery(db: Session, delivery_req: DeliveryRequest) -> list[SendRequest]:
    return db.query(SendRequest).filter(
        SendRequest.from_location == delivery_req.from_location,
        SendRequest.to_location == delivery_req.to_location,
        and_(SendRequest.from_date <= delivery_req.delivery_date, 
             delivery_req.delivery_date <= SendRequest.to_date),
        or_(SendRequest.size_type == delivery_req.size_type, delivery_req.size_type == 'Не указаны'),
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