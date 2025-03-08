
from src.database.models.support_req import SupportRequest
from src.database.models import crud
from src.database.connection import db


from src.bot import bot
import src.common.keyboard as kb 

import asyncio
from src.config.env_config import config


async def send_supp_request(supp_req: SupportRequest):
    chat_id = config.SUPPORT_CHAT_ID

    user = crud.get_user_by_tg_id(db, supp_req.user.telegram_user.telegram)

    reqs = crud.get_all_req_ids_by_user(db, user)

    text = f'Поступила новая заявка на поддержку от пользователя {user.name} ({user.phone}).'
    text += f'\nНомер заявки: {supp_req.id}'
    text += f'\nТекст заявки: {supp_req.message}'

    tg_user = user.telegram_user
    if tg_user.username:
        text += f'\n\n<b>Информация о пользователе:</b>'
        text += f'\nИмя пользователя: @{tg_user.username}'
        text += f'\nID пользователя: {tg_user.telegram}'
    
    text += f'\n\n<b>Все заявки пользователя:</b>'
    send_ids = reqs['send']
    text += f'\nНа отправку: '
    text += ', '.join([str(i) for i in send_ids]) if send_ids else 'Отсутствуют'
    
    delivery_ids = reqs['delivery']
    text += f'\nНа доставку: ' 
    text += ', '.join([str(i) for i in delivery_ids]) if delivery_ids else 'Отсутствуют'

    await bot.send_message(chat_id, text, parse_mode='HTML')