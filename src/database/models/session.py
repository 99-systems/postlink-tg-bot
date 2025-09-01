from sqlalchemy import Column, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from src.database.connection import Base


class TgSession(Base):
    __tablename__ = "sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="session", uselist=False)

