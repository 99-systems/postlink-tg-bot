from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, or_f
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import F


import src.common.keyboard as kb
import src.context as context
from src.common.states import AppState, RegistrationState
from src.database.models import crud
from src.database import db

from src.utils import get_place

from src.handlers.auth import router, OTP_CODE_LENGTH
from src.handlers.auth.common import handle_success_auth, handle_back_start
from .filters import PhoneNumberFilter
from .utils import format_phone_number

from src.services import sheets 


@router.message(RegistrationState.city, F.text.lower() == 'назад')
@router.message(AppState.auth, or_f(F.text.lower() == 'регистрация', Command('register')))   
async def handle_registration(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.name)
    await message.reply('Как Вас зовут?', reply_markup=kb.back_reply_mu)


@router.message(RegistrationState.name)
@router.message(RegistrationState.city_confirmation, F.text.lower() == 'неверный адрес')
async def handle_name(message: Message, state: FSMContext):

    current_state = await state.get_state()
    
    if current_state == RegistrationState.name:
        await state.update_data(name=message.text)
    
    if message.text.lower() == 'нет':
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
    
    await state.set_state(RegistrationState.city)

    state_data = await state.get_data()
    name = state_data.get('name', message.text)

    text = f'{name}, В каком городе Вы находитесь?\n\n<i>Можно указать название города или отправить свою геолокацию.</i>'

    if 'try_count' in state_data and state_data['try_count'] > 0:
        text = f'{name}, В каком городе Вы находитесь?\n\n<i>Если не можете найти, можно указать страну с городом.\nКазахстан, Алматы</i>'
    await message.answer(text, reply_markup=kb.request_location_and_back_reply_mu, parse_mode='HTML')
    
@router.message(RegistrationState.city)
async def handle_city(message: Message, state: FSMContext):
    
    place = await get_place(message.text, message)
    
    if place:
        await state.set_state(RegistrationState.city_confirmation)
        await message.answer(f'Вы находитесь в городе: {place["display_name"]}?', reply_markup=kb.city_conf_reply_mu)    
        await state.update_data(city=place["display_name"])
    else:
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
        await message.answer('Город не найден. Попробуйте еще раз', reply_markup=kb.request_location_and_back_reply_mu)

    
@router.message(RegistrationState.city_confirmation, F.text.lower() == 'да')
async def handle_city_confirmation(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.phone)
    await message.answer('Можно узнать Ваш сотовый номер телефона?', reply_markup=kb.phone_reply_mu)
    
    
    
@router.message(RegistrationState.phone, PhoneNumberFilter())
async def handle_phone_number(message: Message, state: FSMContext):
    
    user_phone = format_phone_number(message.contact.phone_number if message.contact else message.text)
    await state.update_data(phone=user_phone)
    
    user = crud.get_user_by_phone(db, user_phone)
    if user:
        await message.reply('Пользователь с таким номером телефона уже существует, попробуйте войти')
        await state.set_state({}) 
        await handle_back_start(message, state)
        return
    
    response = await context.otp_service.send_otp(user_phone, OTP_CODE_LENGTH)
    if 'message' in response:
        await message.reply(f'Я выслал Вам код подтверждения на WhatsApp по номеру {user_phone}. Прошу отправить мне полученный 4-х значный код.', reply_markup=ReplyKeyboardRemove())
        await state.update_data(phone=user_phone)
        await state.set_state(RegistrationState.otp_code)
    else:
        await message.reply('Попробуйте еще раз')
        await state.set_state(RegistrationState.phone)
        return
    
@router.message(RegistrationState.otp_code, F.text.len() != OTP_CODE_LENGTH)
async def handle_invalid_otp_code(message: Message, state: FSMContext):
    await message.reply('Это не похоже на 4-х значный код, попробуйте еще раз')
    await state.set_state(RegistrationState.otp_code)

@router.message(RegistrationState.otp_code, F.text.len() == OTP_CODE_LENGTH, F.text.func(str.isdigit))
async def handle_otp_code(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get('phone')
    
    response = await context.otp_service.verify_otp(phone, message.text)

    # Обработка ошибок верификации OTP
    error_messages = {
        'OTP has expired. Please request a new one.': (RegistrationState.phone, 'Код устарел, запросите новый код'),
        'OTP has already been used.': (RegistrationState.phone, 'Код уже использован, запросите новый код'),
        'Invalid OTP or phone number.': (RegistrationState.otp_code, 'Неверный код. Попробуйте еще раз')
    }

    if 'detail' in response:
        state_target, error_msg = error_messages.get(response['detail'], (RegistrationState.phone, 'Ошибка при верификации кода'))
        await message.reply(error_msg)
        await state.set_state(state_target)
        return

    # Если OTP успешно подтвержден
    if response.get('message') == 'OTP verified successfully':
        try:
            user = crud.create_user(db, phone=phone, name=data.get('name'), city=data.get('city'))
            print('do set')
            crud.set_user_id_for_tg_user(db, message.from_user.id, user.id)
            print('do session')
            crud.create_session(db, user_id=user.id)
            print('do rec')
            sheets.record_add_user(user)
            
        except Exception as e:
            print(e)
            await message.reply('Ошибка при регистрации пользователя')
            await handle_back_start(message, state)
            return

        await state.clear()
        await handle_success_auth(message, state)
    else:
        await message.reply('Ошибка при обработке OTP. Попробуйте позже.')
        

