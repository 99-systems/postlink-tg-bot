from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

import src.context as context

from src.common import keyboard as kb

from src.database.models import crud
from src.database.models.request import SendRequest, DeliveryRequest

from src.database.connection import db

router = Router()


@router.message(F.text.lower() == "статус заявки")
async def request_status(message: Message, state: FSMContext):
    requests = crud.get_request_by_tg_id(db, message.from_user.id)
    
    if not requests:
        await message.answer("У вас нет активных заявок.")
        return
    
    for request in requests:
        send = isinstance(request, SendRequest)
        
        text = "<b>Заявка на отправку</b>\n" if send else "<b>Заявка на доставку</b>\n"

        status = 'Открыта' if request.status == 'open' else 'Закрыта'
        text += f'Номер заявки {request.id}\nСтатус: {status}\nМаршрут: {request.from_location} - {request.to_location}'
        
        if send:
            from_date = request.from_date.strftime('%d.%m.%Y')
            to_date = request.to_date.strftime('%d.%m.%Y')
            text += f"\nДата: {from_date} - {to_date}\nТип груза: {request.size_type}"
        else:
            delivery_date = request.delivery_date.strftime('%d.%m.%Y')
            text += f"\nДата: {delivery_date}\nТип груза: {request.size_type}"

        await message.answer(text, reply_markup=kb.create_close_req_button('send' if send else 'delivery', request.id), parse_mode='HTML')


@router.message(F.text.lower() == "отменить заявку")
async def close_request(message: Message, state: FSMContext):
    await request_status(message, state)

@router.callback_query(F.data.startswith('close_req'))
async def close_request_kb(callback: CallbackQuery, state: FSMContext):
    req_data = callback.data.split(':')[1:]
    req_id = int(req_data[1])
    req_type = req_data[0]
    await callback.answer()
    if req_type == 'send':
        crud.close_send_request(db, req_id)
    elif req_type == 'delivery': 
        crud.close_delivery_request(db, req_id)
    else:
        await callback.answer('Ошибка при закрытии заявки')
        return
    
    req_type_text = 'отправку' if req_type == 'send' else 'доставку'
    await callback.message.answer(f'Заявка на {req_type_text} по номеру {req_id} закрыта.')