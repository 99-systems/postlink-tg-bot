import asyncio
from src.bot import bot, dp
from src.handlers import main as main_handler, auth as auth_handler, support as support_handler, menu as menu_handler
from src.handlers import send_request as send_request_handler
from src.handlers import deliver_request as deliver_request_handler
from src.handlers import manage_request as manage_request_handler
from src.handlers import admin as admin_handler

from src.handlers import main as main_handler, auth as auth_handler, support as support_handler, menu as menu_handler
from src.middlewares.auth_middleware import AuthMiddlewareMessage
from src.middlewares.not_auth_middleware import NotAuthMiddlewareMessage
from src.middlewares.open_request import OpenRequestMessageMiddleware, OpenRequestCallbackMiddleware

async def run():

    
    # Middleware configuration
    main_handler.router.message.middleware(AuthMiddlewareMessage()) #проверяеть на не залогиененного пользователя
    # main_handler.router.callback_query.middleware(AuthMiddlewareMessage())
    auth_handler.router.message.middleware(NotAuthMiddlewareMessage()) #проверяет на залогиненного пользователя и он больше не зайти в авторизовацию
    send_request_handler.router.message.middleware(OpenRequestMessageMiddleware()) #проверяет на наличие открытой заявки
    deliver_request_handler.router.message.middleware(OpenRequestMessageMiddleware()) #проверяет на наличие открытой заявки

    # Router configuration
    menu_handler.router.include_routers(
        support_handler.router,
        send_request_handler.router,
        deliver_request_handler.router,
        manage_request_handler.router,
        admin_handler.router
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