from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from src.database.models import crud
from src.database.connection import db
from src.handlers.menu import menu

class NotAuthMiddlewareMessage(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        user_id = event.from_user.id
        
        if user_id and crud.is_tg_user_exists(db, user_id):
            await menu(event, data.get("state"))
            return
        
        return await handler(event, data)         
