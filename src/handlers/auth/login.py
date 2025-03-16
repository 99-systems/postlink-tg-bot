from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, or_f
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import F


import src.common.keyboard as kb
import src.context as context
from src.common.states import AppState, LoginState
from src.database.models import crud
from src.database import db


from src.handlers.auth import router, OTP_CODE_LENGTH
from src.handlers.auth.common import handle_success_auth, handle_back_start
from .filters import PhoneNumberFilter
from .utils import format_phone_number


@router.message(AppState.auth, or_f(F.text.lower() == 'авторизация', Command('login')))
async def handle_login(message: Message, state: FSMContext):
    await state.set_state(LoginState.phone)
    await message.answer('Можно узнать Ваш сотовый номер телефона, привязанный к WhatsApp?', reply_markup=kb.phone_reply_mu)
    
@router.message(LoginState.phone, PhoneNumberFilter())
async def handle_phone_number(message: Message, state: FSMContext):
    
    user_phone = format_phone_number(message.contact.phone_number if message.contact else message.text)
    await state.update_data(phone=user_phone)
    
    user = crud.get_user_by_phone(db, user_phone)
    if not user:
        await message.reply('Пользователь с таким номером телефона не найден, попробуйте зарегистрироваться')
        await state.set_state({}) 
        await handle_back_start(message, state)
        return
    
    response = await context.otp_service.send_otp(user_phone, OTP_CODE_LENGTH)
    if 'message' in response:
        await message.reply(f'Я выслал Вам код подтверждения на WhatsApp по номеру {user_phone}. Прошу отправить мне полученный 4-х значный код.', reply_markup=ReplyKeyboardRemove())
        await state.update_data(phone=user_phone)
        await state.set_state(LoginState.otp_code)
    else:
        await message.reply('Попробуйте еще раз')
        await state.set_state(LoginState.phone)
        return

@router.message(LoginState.otp_code, F.text.len() != OTP_CODE_LENGTH)
async def handle_invalid_otp_code(message: Message, state: FSMContext):
    await message.reply('Это не похоже на 4-х значный код, попробуйте еще раз')
    await state.set_state(LoginState.otp_code)

@router.message(LoginState.otp_code, F.text.len() == OTP_CODE_LENGTH, F.text.func(str.isdigit))
async def handle_otp_code(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get('phone')

    response = await context.otp_service.verify_otp(phone, message.text)

    # Словарь для обработки ошибок
    error_messages = {
        'OTP has expired. Please request a new one.': (LoginState.phone, 'Код устарел, запросите новый код'),
        'OTP has already been used.': (LoginState.phone, 'Код уже использован, запросите новый код'),
        'Invalid OTP or phone number.': (LoginState.otp_code, 'Неверный код. Попробуйте еще раз'),
    }

    if 'detail' in response:
        state_target, error_msg = error_messages.get(response['detail'], (LoginState.phone, 'Ошибка при верификации кода'))
        await message.reply(error_msg)
        await state.set_state(state_target)
        return

    # Проверка успешной верификации OTP
    if response.get('message') == 'OTP verified successfully':
        await state.clear() 
        try: 
            user = crud.get_user_by_phone(db, phone)
            crud.create_session(db, user.id)
        except Exception as e:
            await message.reply('Ошибка при авторизации пользователя')
            await handle_back_start(message, state)
            return
        await handle_success_auth(message, state)
    else:
        await message.reply('Ошибка при обработке OTP. Попробуйте позже.')