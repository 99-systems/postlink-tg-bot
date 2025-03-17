import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_NAME = os.getenv("BOT_NAME")
    DATABASE_URL = os.getenv("DATABASE_URL")
    NOMINATIM_API_URL = os.getenv("NOMINATIM_API_URL")
    OTP_API_KEY = os.getenv("OTP_SERVICE_API_KEY")
    OTP_SERVICE_URL = os.getenv("OTP_SERVICE_URL")
    DEBUG = os.getenv('DEBUG')
    SUPPORT_CHAT_ID = os.getenv('SUPPORT_CHANNEL_CHAT_ID')
    MONGO_HOST = os.getenv('MONGO_HOST')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
    MONGO_USER = os.getenv('MONGO_USER')
    GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')

config = Config()

