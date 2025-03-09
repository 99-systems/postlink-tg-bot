
from src.database.models.request import SendRequest, DeliveryRequest
from src.database.models import crud
from src.database.connection import db


from src.bot import bot
import src.common.keyboard as kb 

async def match_send_request(send_req: SendRequest):
    delivery_reqs = crud.get_matched_requests_for_send(db, send_req)
    for delivery_req in delivery_reqs:
        await send_request_notify(send_req, delivery_req)

    return


async def match_delivery_request(delivery_req: DeliveryRequest):
    send_reqs = crud.get_matched_requests_for_delivery(db, delivery_req)
    for send_req in send_reqs:
        await send_request_notify(send_req, delivery_req)
        
    return

async def send_request_notify(send_req: SendRequest, delivery_req: DeliveryRequest):
    text = f'Мы нашли вам отправителя! По номеру заявки {delivery_req.id}. '
    text += f'\n<b>Информация от отправителя:</b>\nМаршрут: {send_req.from_location} - {send_req.to_location}'
    text += f'\nВес и габариты: {send_req.size_type}'

    if send_req.description != 'Пропустить':
        text += f'\nДополнительные требования: {send_req.description}'

    await bot.send_message(delivery_req.user.telegram_user.telegram, 
                           text, reply_markup=kb.create_send_req_buttons(send_req.id),
                           parse_mode='HTML')
    return