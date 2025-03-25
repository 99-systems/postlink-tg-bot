from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.common import keyboard as kb
from src.database.models import crud
from src.database.models.request import SendRequest
from src.database import db

from src.services import sheets
from src.bot import bot

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
        
        from_date = request.from_date.strftime('%d.%m.%Y')
        to_date = request.to_date.strftime('%d.%m.%Y')
        text += f"\nДата: {from_date} - {to_date}\nТип груза: {request.size_type}"

        await message.answer(text, reply_markup=kb.create_close_req_button('send' if send else 'delivery', request.id), parse_mode='HTML')


@router.message(F.text.lower() == "отменить заявку")
async def close_request(message: Message, state: FSMContext):
    await request_status(message, state)

from .callbacks import RequestCallback, Action, User

@router.callback_query(RequestCallback.filter(F.user == User.sender), RequestCallback.filter(F.action == Action.accept))
async def accept_request_from_sender_kb(callback: CallbackQuery, callback_data: RequestCallback):
    
    
    await callback.message.delete()
    
    sender_user_tg_id = callback.from_user.id
    sender_user = crud.get_user_by_tg_id(db, sender_user_tg_id)
    sender_contact_info = "Контакты отправителя:\n"
    if sender_user.name:
        sender_contact_info += f"Контактное имя: {sender_user.name}\n"
    if sender_user.phone:
        sender_contact_info += f"Телефон: {sender_user.phone}\n"
    if sender_user.telegram_user.username:
        sender_contact_info += f"Telegram: @{sender_user.telegram_user.username} "
    if sender_user.telegram_user.telegram:
        sender_contact_info += f"(ID: {sender_user.telegram_user.telegram})"
    
    delivery_user_id = callback_data.delivering_user_id
    delivery_user = crud.get_user_by_id(db, delivery_user_id)
    
    crud.close_delivery_request(db, callback_data.delivery_request_id)
    sheets.record_close_deliver_req(callback_data.delivery_request_id)
    reply_markup = (kb.main_menu_open_req_reply_mu 
                if crud.is_open_request_by_tg_id(db, delivery_user.telegram_user.telegram) 
                else kb.main_menu_reply_mu)
    
    await bot.send_message(delivery_user.telegram_user.telegram, f'Отправитель принял ваше предложение. Свяжитесь с ним для уточнения деталей доставки.\n{sender_contact_info}')
    await bot.send_message(delivery_user.telegram_user.telegram, 'Ваша заявка на доставку была закрыта.', reply_markup=reply_markup)
    
    delivery_user_contact_info = "Контакты курьера:\n"
    if delivery_user.name:
        delivery_user_contact_info += f"Контактное имя: {delivery_user.name}\n"
    if delivery_user.phone:
        delivery_user_contact_info += f"Телефон: {delivery_user.phone}\n"
    if delivery_user.telegram_user.username:
        delivery_user_contact_info += f"Telegram: @{delivery_user.telegram_user.username} "
    if delivery_user.telegram_user.telegram:
        delivery_user_contact_info += f"(ID: {delivery_user.telegram_user.telegram})"
    crud.close_send_request(db, callback_data.send_request_id)
    sheets.record_close_send_req(callback_data.send_request_id)
    reply_markup = (kb.main_menu_open_req_reply_mu 
                if crud.is_open_request_by_tg_id(db, sender_user.telegram_user.telegram) 
                else kb.main_menu_reply_mu)
    await callback.message.answer(f'Ваше предложение принято. Свяжитесь с курьером для уточнения деталей доставки.\n{delivery_user_contact_info}')
    await callback.message.answer('Ваша заявка на отправку была закрыта.', reply_markup=reply_markup)

@router.callback_query(RequestCallback.filter(F.user == User.sender), RequestCallback.filter(F.action == Action.reject))
async def reject_request_from_sender_kb(callback: CallbackQuery, callback_data: RequestCallback):    
    
    await callback.message.delete()
    await callback.answer('Заявка отклонена.')


@router.callback_query(RequestCallback.filter(F.user == User.delivery), RequestCallback.filter(F.action == Action.accept))
async def accept_request_from_delivery_kb(callback: CallbackQuery, callback_data: RequestCallback):
    
    await callback.message.delete()
    
    reply_markup = (kb.main_menu_open_req_reply_mu 
                    if crud.is_open_request_by_tg_id(db, callback.message.from_user.id) 
                    else kb.main_menu_reply_mu)
    
    
    send_req_id = callback_data.send_request_id
    send_req = crud.get_send_request_by_id(db, send_req_id)
    
    # Check if sending request is still open
    if send_req.status != 'open':
        await callback.message.delete()
        await callback.answer('Заявка на отправку уже закрыта.')
        return
    
    # Request is open, proceed with matching
    tg_id_of_send_req = send_req.user.telegram_user.telegram
    delivery_user = crud.get_user_by_id(db, callback_data.delivering_user_id)
    
    await bot.send_message(tg_id_of_send_req, 'Курьер готов взять ваш заказ.', reply_markup=kb.create_accept_buttons_for_sender(send_req_id, callback_data.delivery_request_id, send_req.user_id, delivery_user.id))    
    
    await callback.message.answer('Ваше предложение принято и отправлено отправителю. Ожидайте его ответа. В случае одобрения заявки вы получите сообщение с контактными данными отправителя.', reply_markup=reply_markup)
    await callback.answer()
    

@router.callback_query(RequestCallback.filter(F.user == User.delivery), RequestCallback.filter(F.action == Action.reject))
async def reject_request_from_delivery_kb(callback: CallbackQuery, callback_data: RequestCallback):    
    
    await callback.message.delete()
    await callback.answer('Заявка отклонена.')
    

@router.callback_query(F.data.startswith('close_req'))
async def close_request_kb(callback: CallbackQuery, state: FSMContext):
    req_data = callback.data.split(':')[1:]
    req_id = int(req_data[1])
    req_type = req_data[0]
    await callback.answer()
    if req_type == 'send':
        crud.close_send_request(db, req_id)
        sheets.record_close_send_req(req_id)
    elif req_type == 'delivery': 
        crud.close_delivery_request(db, req_id)
        sheets.record_close_deliver_req(req_id)
    else:
        await callback.answer('Ошибка при закрытии заявки')
        return
    
    req_type_text = 'отправку' if req_type == 'send' else 'доставку'
    await callback.message.answer(f'Заявка на {req_type_text} по номеру {req_id} закрыта.', reply_markup=kb.main_menu_reply_mu)