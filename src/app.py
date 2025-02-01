import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import src.config.env_config as env


# all handlers should be defined here
from src.handlers import main as main_handler, auth as auth_handler


async def run():

    bot = Bot(token=env.bot_token)

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)


    # !посмотреть потом 
    # await bot.delete_webhook(drop_pending_updates=True)
    dp.include_routers(
        main_handler.router,
        auth_handler.router
    )
        
    try:
        print('Bot is running')
        asyncio.run(await dp.start_polling(bot))
    except Exception as e:
        print(f'app.py error while polling bot: {e}')