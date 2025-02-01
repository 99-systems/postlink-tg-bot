from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
from src.config.env_config import db_url


# полностью отключить SQLAlchemy логи:
# закоментить если что для дебаггинга
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


engine = create_engine(db_url, echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    """Создаёт таблицы, если их нет"""
    from .models import user 
    Base.metadata.create_all(bind=engine)