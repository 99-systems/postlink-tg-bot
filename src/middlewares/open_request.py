from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from src.database.models import crud
from src.database.connection import db
from src.handlers import menu

class OpenRequestMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            user_id = event.from_user.id
        except Exception as e:
            return await handler(event, data)         

        try:
            if user_id and crud.is_open_request_by_tg_id(db, user_id):
                await event.answer('Вы уже создали заявку. Пожалуйста дождитесь ответа или отмените текущую заявку')
                await menu.handle_menu(event, data.get("state"))
                return
        except Exception as e:
            return await handler(event, data)         
        return await handler(event, data)       

class OpenRequestCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            user_id = event.message.from_user.id
        except Exception as e:
            return await handler(event, data)         

        try:
            if user_id and crud.is_open_request_by_tg_id(db, user_id):
                await event.answer('Вы уже создали заявку. Пожалуйста дождитесь ответа или отмените текущую заявку')
                await menu.handle_menu(event, data.get("state"))
                return
        except Exception as e:
            return await handler(event, data)         
