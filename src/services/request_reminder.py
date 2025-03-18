
from src.database.models.request import SendRequest, DeliveryRequest
from src.database.models import crud
from src.database.connection import db


from src.bot import bot
import src.common.keyboard as kb 

import asyncio
from src.config import config
from typing import Union


async def send_request(req: Union[SendRequest, DeliveryRequest]):
    chat_id = config.REQUESTS_CHAT_ID

    user = crud.get_user_by_tg_id(db, req.user.telegram_user.telegram)
    tg_user = user.telegram_user

    text = f"📄 <b>Новая заявка</b>\n"
    text += f"🔢 <b>Номер заявки:</b> {req.id}\n"
    text += f"👤 <b>Пользователь:</b> {user.name} ({user.phone})\n"

    text += f"🌐 <b>Telegram:</b> @{tg_user.username} (ID: {tg_user.telegram})\n"

    if isinstance(req, SendRequest):
        text += f"🚚 <b>Тип заявки:</b> Отправка\n"
        text += f"📍 <b>Откуда:</b> {req.from_location}\n"
        text += f"🏁 <b>Куда:</b> {req.to_location}\n"
        text += f"📅 <b>Дата отправки с:</b> {req.from_date.strftime('%Y-%m-%d %H:%M')}\n"
        text += f"📅 <b>Дата отправки до:</b> {req.to_date.strftime('%Y-%m-%d %H:%M')}\n"
    elif isinstance(req, DeliveryRequest):
        text += f"🚚 <b>Тип заявки:</b> Доставка\n"
        text += f"📍 <b>Откуда:</b> {req.from_location}\n"
        text += f"🏁 <b>Куда:</b> {req.to_location}\n"
        text += f"📅 <b>Дата отправления:</b> {req.delivery_date.strftime('%Y-%m-%d %H:%M')}\n"

    if req.size_type:
        text += f"📦 <b>Вес и габариты:</b> {req.size_type}\n"
    if hasattr(req, "description") and req.description:
        text += f"📝 <b>Описание:</b> {req.description}\n"

    text += f"🟢 <b>Статус:</b> {req.status}\n"

    text += f"🕒 <b>Создано:</b> {req.created_at.strftime('%Y-%m-%d %H:%M')}\n"

    await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')