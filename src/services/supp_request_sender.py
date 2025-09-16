from src.database.models.support_req import SupportRequest
from src.database.models import crud
from src.database.connection import get_db


from src.bot import bot
import src.common.keyboard as kb 

import asyncio
from src.config import config


async def send_supp_request(supp_req: SupportRequest):
    chat_id = config.SUPPORT_CHAT_ID

    user = None
    if supp_req.user:
        with get_db() as db:
            user = crud.get_user_by_tg_id(db, supp_req.user.telegram_user.telegram)
    
    if user:
        # reqs = crud.get_all_req_ids_by_user(db, user)
        text = f'Поступила новая заявка на поддержку от пользователя {user.name} ({user.phone}).'
    else:
        tg_user = supp_req.telegram_user
        if tg_user:
            username = f"@{tg_user.username}" if hasattr(tg_user, 'username') and tg_user.username else "без имени пользователя"
            text = f'Поступила новая заявка на поддержку от пользователя с ID {tg_user.telegram} и {username}.'
        else:
            text = 'Поступила новая заявка на поддержку от неизвестного пользователя.'

    text += f'\nТекст заявки: {supp_req.message}'



    if user:
        tg_user = user.telegram_user
        if hasattr(tg_user, 'username') and tg_user.username:
            text += f'\n\n<b>Информация о пользователе:</b>'
            text += f'\nИмя пользователя: @{tg_user.username}'
            text += f'\nID пользователя: {tg_user.telegram}'
        
        # text += f'\n\n<b>Все заявки пользователя:</b>'
        # send_ids = reqs['send']
        # text += f'\nНа отправку: '
        # text += ', '.join([str(i) for i in send_ids]) if send_ids else 'Отсутствуют'
        #
        # delivery_ids = reqs['delivery']
        # text += f'\nНа доставку: '
        # text += ', '.join([str(i) for i in delivery_ids]) if delivery_ids else 'Отсутствуют'

    await bot.send_message(chat_id, text, parse_mode='HTML')

async def send_message_to_user(telegram_id: int, message: str):
    await bot.send_message(telegram_id, message, reply_markup=kb.admin_support_reply_mu(telegram_id))

async def send_message_to_admins(message: str):
    for admin in config.ADMINS:
        await bot.send_message(admin, message)
        await asyncio.sleep(0.1)

async def send_message_to_all_users(message: str):
    with get_db() as db:
        users = crud.get_all_users(db)
    for user in users:
        try:
            await bot.send_message(user.telegram_user.telegram, message)
            await asyncio.sleep(0.1)
        except Exception as e:
            print(e)
            continue
        
async def get_user_id_from_request(message: str):
    try:
        user_id = int(message.split('\n')[1].split(' ')[-1])
        return user_id
    except:
        return None
    
async def get_user_from_request(message: str):
    try:
        user_id = await get_user_id_from_request(message)
        if user_id:
            with get_db() as db:
                return crud.get_user_by_tg_id(db, user_id)
    except:
        return None
    
async def get_supp_request_from_message(message: str):
    try:
        supp_req_id = int(message.split('\n')[0].split(' ')[-1])
        with get_db() as db:
            return crud.get_supp_request_by_id(db, supp_req_id)
    except:
        return None
    
async def close_supp_request(message: str):
    supp_req = await get_supp_request_from_message(message)
    if supp_req:
        with get_db() as db:
            crud.close_supp_request(db, supp_req)
        await bot.send_message(supp_req.telegram_user.telegram, 'Ваша заявка в поддержку была закрыта.')
        return True
    return False
    
async def get_message_from_supp_request(message: str):
    try:
        return message.split('Ответ: ')[1]
    except:
        return None
    
async def get_user_id_from_supp_request(message: str):
    try:
        return int(message.split('\n')[1].split(' ')[-1])
    except:
        return None
    
async def answer_to_supp_request(message: str):
    user_id = await get_user_id_from_supp_request(message)
    answer = await get_message_from_supp_request(message)
    if user_id and answer:
        await send_message_to_user(user_id, answer)
        return True
    return False