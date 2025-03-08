import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.config import config
from src.handlers import main as main_handler, auth as auth_handler, support as support_handler, parcel as parcel_handler, menu as menu_handler
from src.middlewares.auth_middleware import AuthMiddlewareMessage
from src.middlewares.not_auth_middleware import NotAuthMiddlewareMessage


async def run():
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Middleware configuration
    main_handler.router.message.middleware(AuthMiddlewareMessage()) #проверяеть на не залогиененного пользователя
    # main_handler.router.callback_query.middleware(AuthMiddlewareMessage())
    auth_handler.router.message.middleware(NotAuthMiddlewareMessage()) #проверяет на залогиненного пользователя и он больше не зайти в авторизовацию

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