import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    NOMINATIM_API_URL = os.getenv("NOMINATIM_API_URL")
    OTP_API_KEY = os.getenv("OTP_SERVICE_API_KEY")
    OTP_SERVICE_URL = os.getenv("OTP_SERVICE_URL")
    DEBUG = os.getenv('DEBUG')
    SUPPORT_CHAT_ID = os.getenv('SUPPORT_CHANNEL_CHAT_ID')
    MONGO_HOST = os.getenv('MONGO_HOST')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
    MONGO_USER = os.getenv('MONGO_USER')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
    GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
    REQUESTS_CHAT_ID = os.getenv('REQUESTS_CHAT_ID')
    SERVICE_ACCOUNT_CREDS = os.getenv('SERVICE_ACCOUNT_CREDS')
    ADMINS = os.getenv('ADMINS')

config = Config()

