from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from src.common.states import ManageRequestState, AppState
from src.common import keyboard as kb
from src.database.models import crud
from src.database.models.request import SendRequest
from src.database import db

from src.services import sheets
from src.bot import bot
from src.handlers import menu


router = Router()


@router.message(F.text.lower() == "статус заявки")
@router.message(F.text.lower() == "статус заявок")
async def request_status(message: Message, state: FSMContext):
    requests = crud.get_request_by_tg_id(db, message.from_user.id)
    
    if not requests:
        await message.answer("У вас нет активных заявок.")
        return
    
    sent_message_ids = []
    
    for request in requests:
        send = isinstance(request, SendRequest)
        
        text = "📦<b>Заявка на поиск курьера</b>\n" if send else "📦<b>Заявка на поиск заказа (Посылки)</b>\n"

        status = 'Активна' if request.status == 'open' else 'Неактивна'
        text += f'📌Номер заявки {request.id}\n🛎Статус: <b>{status}</b>\n🛫Город отправления: <b>{request.from_location}</b>\n🛫Город назначения: <b>{request.to_location}</b>'
        
        from_date = request.from_date.strftime('%d.%m.%Y')
        to_date = request.to_date.strftime('%d.%m.%Y')
        text += f"\n🗓Даты: <b>{from_date} - {to_date}</b>\n📊Категория посылки: <b>{request.size_type}</b>"
        
        if send:
            text += f"\n📜Дополнительные примечания: <b>{request.description}</b>"
        

        sent_message = await message.answer(text, reply_markup=kb.create_close_req_button('send' if send else 'delivery', request.id), parse_mode='HTML')
        
        sent_message_ids.append(sent_message.message_id)

    await state.update_data(sent_messages_for_close_req=sent_message_ids)


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
    reply_markup = kb.create_main_menu_markup(callback.from_user.id)
    
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
    reply_markup = kb.create_main_menu_markup(callback.from_user.id)
    await callback.message.answer(f'Ваше предложение принято. Свяжитесь с курьером для уточнения деталей доставки.\n{delivery_user_contact_info}')
    await callback.message.answer('Ваша заявка на отправку была закрыта.', reply_markup=reply_markup)

@router.callback_query(RequestCallback.filter(F.user == User.sender), RequestCallback.filter(F.action == Action.reject))
async def reject_request_from_sender_kb(callback: CallbackQuery, callback_data: RequestCallback, state: FSMContext):    
    
    await callback.message.answer('Жаль! Видимо, курьер не подошел по каким-либо параметрам. Тогда продолжаем поиск?', reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Да')], [KeyboardButton(text='Закрыть заявку')]], resize_keyboard=True))
    await callback.message.delete()
    await state.update_data(reject_request_user_type='sender')
    await state.update_data(callback_data=callback_data.to_dict())
    await state.set_state(ManageRequestState.ask_to_continue)
    
@router.message(ManageRequestState.ask_to_continue, F.text.lower() == 'да')
async def handle_continue_search(message: Message, state: FSMContext):
    state_data = await state.get_data()
    callback_data = state_data.get('callback_data')
    reject_request_user_type = state_data.get('reject_request_user_type')
    
    
    if reject_request_user_type == 'sender':
        send_req_id = callback_data['send_request_id']
        req = crud.get_send_request_by_id(db, send_req_id)
        text += "\n<b>📦Заявка на поиск заказа (Посылки)</b>"
    elif reject_request_user_type == 'delivery':
        delivery_req_id = callback_data['delivery_request_id']
        req = crud.get_delivery_request_by_id(db, delivery_req_id)
        text += "\n<b>📦Заявка на поиск курьера</b>"
    
    text += f"\n📌Номер заявки:<b>{req.id}</b>"
    text += f"\n🛎Статус: <b>{req.status}</b>"
    text += f"\n🛫Город отправления: <b>{req.from_location}</b>"
    text += f"\n🛫Город назначения: <b>{req.to_location}</b>"
    text += f"\n🗓Даты: <b>{req.from_date.strftime('%d.%m.%Y')} - {req.to_date.strftime('%d.%m.%Y')}</b>"
    text += f"\n📊Категория: <b>{req.size_type}</b>"
    if req.description != 'Пропустить':
        text += f"\n📜Дополнительные примечания: <b>{req.description}</b>"
    else:
        text += f"\n📜Дополнительные примечания: <b>Нету</b>"
    
    await message.answer(f'Понял! Тогда Ваша заявка остается активной. Детали заявки:{text}', reply_markup=kb.create_main_menu_markup(message.from_user.id), parse_mode='HTML')
    await state.set_state(AppState.menu)

@router.message(ManageRequestState.ask_to_continue, F.text.lower() == 'закрыть заявку')
async def handle_close_request(message: Message, state: FSMContext):
    state_data = await state.get_data()
    callback_data = state_data.get('callback_data')
    reject_request_user_type = state_data.get('reject_request_user_type')
    
    if reject_request_user_type == 'sender':
        send_req_id = callback_data['send_request_id']
        crud.close_send_request(db, send_req_id)
        sheets.record_close_send_req(send_req_id)
        await message.answer('Ваша заявка на отправку была закрыта.', reply_markup=kb.create_main_menu_markup(message.from_user.id))
    elif reject_request_user_type == 'delivery':
        delivery_req_id = callback_data['delivery_request_id']
        crud.close_delivery_request(db, delivery_req_id)
        sheets.record_close_deliver_req(delivery_req_id)
        await message.answer('Ваша заявка на доставку была закрыта.', reply_markup=kb.create_main_menu_markup(message.from_user.id))
    else:
        await message.answer('Ошибка при закрытии заявки')
        return
    await state.set_state(AppState.menu)

@router.callback_query(RequestCallback.filter(F.user == User.delivery), RequestCallback.filter(F.action == Action.accept))
async def accept_request_from_delivery_kb(callback: CallbackQuery, callback_data: RequestCallback):
    
    await callback.message.delete()
    
    reply_markup = kb.create_main_menu_markup(callback.from_user.id)
    
    
    send_req_id = callback_data.send_request_id
    send_req = crud.get_send_request_by_id(db, send_req_id)
    
    # Check if sending request is still open
    if send_req.status != 'open':
        await callback.message.delete()
        await callback.message.answer('Заявка на отправку уже закрыта.')
        return
    
    # Request is open, proceed with matching
    tg_id_of_send_req = send_req.user.telegram_user.telegram
    delivery_user = crud.get_user_by_id(db, callback_data.delivering_user_id)
    
    delivery_req_id = callback_data.delivery_request_id
    delivery_req = crud.get_delivery_request_by_id(db, delivery_req_id)
    
    delivery_guy_info = f"🛫<b>Город отправления:</b> {delivery_req.from_location}\n🛫<b>Город назначения:</b> {delivery_req.to_location}\n🗓<b>Даты:</b> {delivery_req.from_date.strftime('%d.%m.%Y')} - {delivery_req.to_date.strftime('%d.%m.%Y')}\n📊<b>Категория посылки:</b> {delivery_req.size_type}"
    
    if delivery_req.description != 'Пропустить':
        delivery_guy_info += f"\n📜Дополнительные примечания:</b> {delivery_req.description}"
    else:
        delivery_guy_info += f"\n📜<b>Дополнительные примечания:</b> Нету"
    
    await bot.send_message(tg_id_of_send_req, f'<b>🎉 Поздравляем! По вашей заявке №{send_req_id} найден курьер.</b>\nВот его данные: ', reply_markup=kb.create_accept_buttons_for_sender(send_req_id, callback_data.delivery_request_id, send_req.user_id, delivery_user.id), parse_mode='HTML')    
    
    await callback.message.answer('Ваше предложение принято и отправлено отправителю. Ожидайте его ответа. В случае одобрения заявки вы получите сообщение с контактными данными отправителя.', reply_markup=reply_markup)
    await callback.answer()
    

@router.callback_query(RequestCallback.filter(F.user == User.delivery), RequestCallback.filter(F.action == Action.reject))
async def reject_request_from_delivery_kb(callback: CallbackQuery, callback_data: RequestCallback, state: FSMContext):    
    
    await callback.message.answer('Жаль! Видимо, заказ не подошел по каким-либо параметрам. Тогда продолжаем поиск?', reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Да')], [KeyboardButton(text='Закрыть заявку')]], resize_keyboard=True))
    await callback.message.delete()

    await state.update_data(reject_request_user_type='delivery')
    await state.update_data(callback_data=callback_data.to_dict())
    await state.set_state(ManageRequestState.ask_to_continue)
    
    
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
    
    
    state_data = await state.get_data()
    msgs_to_delete = state_data.get('sent_messages_for_close_req', [])
    for msg_id in msgs_to_delete:    
        await bot.delete_message(callback.from_user.id, msg_id)
    
    await callback.message.answer(f'Заявка на {req_type_text} по номеру {req_id} закрыта.')
    await menu.handle_menu(callback.message, state)