import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import src.config.env_config as env
from src.handlers import main as main_handler, auth as auth_handler, support as support_handler, parcel as parcel_handler, menu as menu_handler

async def run():
    bot = Bot(token=env.bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Router configuration
    menu_handler.router.include_routers(
        support_handler.router,
        parcel_handler.router
    )
    
    main_handler.router.include_router(menu_handler.router)
    
    dp.include_routers(
        auth_handler.router,
        main_handler.router,
    )
        

    
    from src.database.connection import engine, SessionLocal
    from src.database.models.user import User, TelegramUser
    from src.database.connection import init_db

    init_db()


    try:
        print('Bot is running')
        await dp.start_polling(bot)
    except Exception as e:
        print(f'app.py error while polling bot: {e}')

if __name__ == "__main__":
    asyncio.run(run())