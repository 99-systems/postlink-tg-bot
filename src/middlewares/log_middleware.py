from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

class LogMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]):
        fsm_context = data['state']
        print('LogMiddleware, before handler, state:', await fsm_context.get_state())
        try:
            result = await handler(event, data)
            print('LogMiddleware, handler executed successfully')
            return result
        except Exception as e:
            print(f'LogMiddleware, handler error: {e}')
            raise