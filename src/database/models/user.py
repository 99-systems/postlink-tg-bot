from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    code = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    telegram_user = relationship("TelegramUser", back_populates="user", uselist=False)
    send_requests = relationship("SendRequest", back_populates="user", cascade="all, delete-orphan")
    delivery_requests = relationship("DeliveryRequest", back_populates="user", cascade="all, delete-orphan")
    access_user = relationship("AccessUser", back_populates="user", cascade="all, delete-orphan")

class TelegramUser(Base):
    __tablename__ = "telegram_users" 

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)


    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="telegram_user", uselist=False)

class AccessUser(Base):
    __tablename__ = "access_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String, nullable=False, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="access_user", uselist=False)
