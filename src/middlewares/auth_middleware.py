from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from src.database.models import crud
from src.database import db
from src.common import keyboard as kb

class AuthMiddlewareMessage(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        tg_id = event.from_user.id
        
        if tg_id and not crud.get_session_by_tg_id(db, tg_id):
            await event.answer('Вы не авторизованы. Пожалуйста авторизуйтесь', reply_markup=kb.auth_reply_mu)
            return
        
        return await handler(event, data)         
