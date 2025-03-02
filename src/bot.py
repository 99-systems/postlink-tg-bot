
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import src.config.env_config as env

bot = Bot(token=env.bot_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
