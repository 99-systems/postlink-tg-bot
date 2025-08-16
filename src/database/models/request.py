from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database.connection import Base

class SendRequest(Base):
    __tablename__ = "send_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_location = Column(String, nullable=False) 
    to_location = Column(String, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="send_requests")

    from_date = Column(DateTime, nullable=False)  
    to_date = Column(DateTime, nullable=False)
    size_type = Column(String, nullable=True)
    description = Column(String, nullable=True)

    status = Column(String, nullable=False, default="open")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class DeliveryRequest(Base):
    __tablename__ = "delivery_requests"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_location = Column(String, nullable=False)  
    to_location = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="delivery_requests")

    from_date = Column(DateTime, nullable=False)  
    to_date = Column(DateTime, nullable=False)
    size_type = Column(String, nullable=True)
    description = Column(String, nullable=True)

    status = Column(String, nullable=False, default="open")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))