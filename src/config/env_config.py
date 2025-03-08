import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_NAME = os.getenv("BOT_NAME")
    DATABASE_URL = os.getenv("DATABASE_URL")
    PLACES_API_KEY = os.getenv("PLACES_API_KEY")
    PLACES_BASE_URL = os.getenv("PLACES_BASE_URL")
    OTP_API_KEY = os.getenv("OTP_SERVICE_API_KEY")
    OTP_SERVICE_URL = os.getenv("OTP_SERVICE_URL")
    DEBUG = os.getenv('DEBUG')

config = Config()

