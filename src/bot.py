
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.mongo import MongoStorage
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import config

bot = Bot(token=config.BOT_TOKEN)
storage = MongoStorage(client=AsyncIOMotorClient(f"mongodb+srv://{config.MONGO_USER}:{config.MONGO_PASSWORD}@{config.MONGO_HOST}"))
dp = Dispatcher(storage=storage)