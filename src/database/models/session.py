from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.database.connection import Base


class TgSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="session", uselist=False)

