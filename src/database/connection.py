from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
from src.config.env_config import db_url
from src.config.env_config import debug_mode


# полностью отключить SQLAlchemy логи:
if debug_mode == "true":
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


engine = create_engine(db_url, echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

db = SessionLocal()


def init_db():
    """Создаёт таблицы, если их нет"""
    from .models.user import User, TelegramUser 
    from .models.request import SendRequest, DeliveryRequest
    Base.metadata.create_all(bind=engine)

