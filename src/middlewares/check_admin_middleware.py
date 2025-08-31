from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from src.database.models import crud
from src.database.connection import get_db

class AdminOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        with get_db() as db:
            user = crud.get_user_by_tg_id(db, user_id)
            if user and user.access_user:
                is_admin = any(access.role == "admin" for access in user.access_user)
                if is_admin:
                    return await handler(event, data)

        await event.answer("У вас нет прав для выполнения этой команды.")
        return