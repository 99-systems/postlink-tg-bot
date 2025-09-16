from src.database.models.support_req import SupportRequest
from src.database.models import crud
from src.database.connection import get_db


from src.bot import bot
import src.common.keyboard as kb 

import asyncio
from src.config import config


async def send_supp_request(supp_req_id: int):
    chat_id = config.SUPPORT_CHAT_ID

    with get_db() as db:
        supp_req = crud.get_supp_request_by_id(db, supp_req_id)
        if not supp_req:
            return

        user = None
        user_name = None
        user_phone = None
        user_tg_username = None
        user_tg_id = None
        tg_username = None
        tg_id = None
        message = supp_req.message

        if supp_req.user:
            user = crud.get_user_by_tg_id(db, supp_req.user.telegram_user.telegram)
            if user:
                user_name = user.name
                user_phone = user.phone
                if user.telegram_user:
                    user_tg_username = user.telegram_user.username
                    user_tg_id = user.telegram_user.telegram

        if supp_req.telegram_user:
            tg_username = supp_req.telegram_user.username
            tg_id = supp_req.telegram_user.telegram

    if user_name and user_phone:
        text = f'Поступила новая заявка на поддержку от пользователя {user_name} ({user_phone}).'
    else:
        if tg_id:
            username_text = f"@{tg_username}" if tg_username else "без имени пользователя"
            text = f'Поступила новая заявка на поддержку от пользователя с ID {tg_id} и {username_text}.'
        else:
            text = 'Поступила новая заявка на поддержку от неизвестного пользователя.'

    text += f'\nТекст заявки: {message}'

    if user_name and user_tg_username and user_tg_id:
        text += f'\n\n<b>Информация о пользователе:</b>'
        text += f'\nИмя пользователя: @{user_tg_username}'
        text += f'\nID пользователя: {user_tg_id}'

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
        user_telegrams = [user.telegram_user.telegram for user in users if user.telegram_user]

    for telegram_id in user_telegrams:
        try:
            await bot.send_message(telegram_id, message)
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
        telegram_id = None
        with get_db() as db:
            # Get fresh support request with relationships
            fresh_supp_req = crud.get_supp_request_by_id(db, supp_req.id)
            if fresh_supp_req and fresh_supp_req.telegram_user:
                telegram_id = fresh_supp_req.telegram_user.telegram
                crud.close_supp_request(db, fresh_supp_req)

        if telegram_id:
            await bot.send_message(telegram_id, 'Ваша заявка в поддержку была закрыта.')
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