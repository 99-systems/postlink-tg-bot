from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String, nullable=True, unique=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    telegram_user = relationship("TelegramUser", back_populates="user", uselist=False)
    session = relationship("TgSession", back_populates="user", uselist=False)
    send_requests = relationship("SendRequest", back_populates="user", cascade="all, delete-orphan")
    delivery_requests = relationship("DeliveryRequest", back_populates="user", cascade="all, delete-orphan")
    support_requests = relationship("SupportRequest", back_populates="user", cascade="all, delete-orphan")
    access_user = relationship("AccessUser", back_populates="user", cascade="all, delete-orphan")

class TelegramUser(Base):
    __tablename__ = "telegram_users" 

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    image = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="telegram_user", uselist=False)
    support_requests = relationship("SupportRequest", back_populates="telegram_user", cascade="all, delete-orphan")


class AccessUser(Base):
    __tablename__ = "access_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String, nullable=False, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="access_user", uselist=False)
