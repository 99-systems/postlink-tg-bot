from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database.connection import Base

class SupportRequest(Base):
    __tablename__ = "support_requests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    telegram_user_id = Column(BigInteger, ForeignKey("telegram_users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="support_requests")
    telegram_user = relationship("TelegramUser", back_populates="support_requests")

    req_type = Column(String, nullable=True)
    req_id = Column(BigInteger, nullable=True)
    
    message = Column(String, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

