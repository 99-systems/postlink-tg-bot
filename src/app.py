import asyncio
from src.bot import bot, dp

from src.handlers.request import send_request as send_request_handler, deliver_request as deliver_request_handler, manage_request as manage_request_handler
from src.handlers import main as main_handler, auth as auth_handler, support as support_handler, menu as menu_handler, admin as admin_handler

from src.middlewares import AuthMiddlewareMessage, LogMiddleware, NotAuthMiddlewareMessage, OpenRequestMessageMiddleware
from src.middlewares.open_request import OpenRequestCallbackMiddleware


async def run():

    
    # Middleware configuration
    main_handler.router.message.middleware.register(LogMiddleware())
    # main_handler.router.message.middleware.register(AuthMiddlewareMessage())    
    auth_handler.router.message.middleware.register(LogMiddleware())
    # auth_handler.router.message.middleware.register(NotAuthMiddlewareMessage()) #проверяет на залогиненного пользователя и он больше не зайти в авторизовацию
    
    menu_handler.router.message.middleware.register(LogMiddleware())
    menu_handler.router.message.middleware.register(AuthMiddlewareMessage())
    
    send_request_handler.router.message.middleware(OpenRequestMessageMiddleware()) #проверяет на наличие открытой заявки
    # send_request_handler.router.callback_query.middleware(OpenRequestCallbackMiddleware()) #проверяет на наличие открытой заявки
    # deliver_request_handler.router.message.middleware(OpenRequestMessageMiddleware()) #проверяет на наличие открытой заявки
    # deliver_request_handler.router.callback_query.middleware(OpenRequestCallbackMiddleware()) #проверяет на наличие открытой заявки


    # Router configuration
    menu_handler.router.include_routers(
        send_request_handler.router,
        deliver_request_handler.router,
        manage_request_handler.router,
        admin_handler.router
    )
    
    main_handler.router.include_routers(
        support_handler.router,
        menu_handler.router
    )
 # Create a global support router that has highest priority
    global_support_router = Router()
    
    @global_support_router.message(F.text.lower() == 'служба поддержки')
    async def handle_global_support(message: Message, state: FSMContext):
        from src.common.states import SupportState
        from src.common import keyboard as kb
        await message.answer('Привет! Это служба поддержки PostLink.\nПожалуйста, ответьте на несколько вопросов, и мы сделаем все, что в наших силах!', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите, кто Вы сейчас⬇️', reply_markup=kb.user_type_reply_mu)
        await state.set_state(SupportState.user_type)

    dp.include_routers(
        global_support_router,  # This router has highest priority
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
