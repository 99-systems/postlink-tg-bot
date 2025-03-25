
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
    text = f'Мы нашли вам отправителя! По вашему номеру заявки на доставку {delivery_req.id}. '
    text += f'\n<b>Информация от отправителя:</b>\nМаршрут: {send_req.from_location} - {send_req.to_location}'
    text += f'\nВес и габариты: {send_req.size_type}'

    if send_req.description != 'Пропустить':
        text += f'\nДополнительные требования: {send_req.description}'

    await bot.send_message(delivery_req.user.telegram_user.telegram, 
                           text, reply_markup=kb.create_accept_buttons_for_delivery(send_req.id, delivery_req.id, send_req.user_id, delivery_req.user_id),
                           parse_mode='HTML')
    return