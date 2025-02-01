import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
bot_name = os.getenv('BOT_NAME')
db_url = os.getenv('DATABASE_URL')
places_api_key = os.getenv('PLACES_API_KEY')
places_base_url = os.getenv('PLACES_BASE_URL')