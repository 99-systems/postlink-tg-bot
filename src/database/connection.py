from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
from src.config import config


# полностью отключить SQLAlchemy логи:
if config.DEBUG == "true":
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


engine = create_engine(config.DATABASE_URL.replace('postgres://', 'postgresql+psycopg2://'), echo=True)
Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

db = SessionLocal()


def init_db():
    """Создаёт таблицы, если их нет"""
    from .models.user import User, TelegramUser 
    from .models.request import SendRequest, DeliveryRequest
    from .models.support_req import SupportRequest
    Base.metadata.create_all(bind=engine)

