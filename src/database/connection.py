from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import config


# полностью отключить SQLAlchemy логи:
# закоментить если что для дебаггинга
# logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
# logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


engine = create_engine(config.DATABASE_URL, echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

db = SessionLocal()


def init_db():
    """Создаёт таблицы, если их нет"""
    from .models.user import User, TelegramUser 
    from .models.request import SendRequest, DeliveryRequest
    Base.metadata.create_all(bind=engine)

