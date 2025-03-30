
from src.database.models.request import SendRequest, DeliveryRequest
from src.database.models import crud
from src.database.connection import db


from src.bot import bot
import src.common.keyboard as kb 

async def match_send_request(send_req: SendRequest):
    delivery_reqs = crud.get_matched_requests_for_send(db, send_req)
    for delivery_req in delivery_reqs:
        await notify_delivery_user(send_req, delivery_req)

    return


async def match_delivery_request(delivery_req: DeliveryRequest):
    send_reqs = crud.get_matched_requests_for_delivery(db, delivery_req)
    for send_req in send_reqs:
        await notify_delivery_user(send_req, delivery_req)
        
    return


async def notify_delivery_user(send_req: SendRequest, delivery_req: DeliveryRequest):
    text = f'🎉 Поздравляем, по Вашей <b>заявке №{delivery_req.id}</b> найден заказ!". '
    text += f'\n<b>Вот данные от отправителя посылки:</b>\n<b>🛫Город отправления:</b> {send_req.from_location}\n<b>🛫Город назначения:</b> {send_req.to_location}\n<b>Даты:</b> {send_req.from_date.strftime("%d.%m.%Y")} - {send_req.to_date.strftime("%d.%m.%Y")}'
    text += f'\n<b>📊Категория посылки:</b> {send_req.size_type}'

    if send_req.description != 'Пропустить':
        text += f'\n<b>📜 Дополнительные примечания:</b> {send_req.description}'
    else:
        text += f'\n<b>📜 Дополнительные примечания:</b> Не указаны'

    await bot.send_message(delivery_req.user.telegram_user.telegram, 
                           text, reply_markup=kb.create_accept_buttons_for_delivery(send_req.id, delivery_req.id, send_req.user_id, delivery_req.user_id),
                           parse_mode='HTML')
    return