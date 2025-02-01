from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from src.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True)
    code = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
