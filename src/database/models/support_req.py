from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database.connection import Base

class SupportRequest(Base):
    __tablename__ = "support_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    telegram_user_id = Column(Integer, ForeignKey("telegram_users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="support_requests")
    telegram_user = relationship("TelegramUser", back_populates="support_requests")

    req_type = Column(String, nullable=True)
    req_id = Column(Integer, nullable=True)
    
    message = Column(String, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

