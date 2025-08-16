import asyncio
from src.bot import bot, dp

from src.handlers import main as main_handler, support as support_handler, admin as admin_handler

from src.middlewares import LogMiddleware


async def run():
    # Middleware configuration
    main_handler.router.message.middleware.register(LogMiddleware())


    # Router configuration
    main_handler.router.include_routers(
        support_handler.router,
        admin_handler.router
    )

    dp.include_routers(
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