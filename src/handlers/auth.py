from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, or_f, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove

from src.common.states import RegistrationState
import src.context as context


from src.common.states import AppState, RegistrationState, LoginState
from src.common import keyboard as kb

from src.database.models import crud
from src.database.connection import db
from src.handlers.menu import menu

router = Router()

# TODO: Ошибка с хранением данных в состоянии FSM



@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(AppState.initial)
    await message.answer('''
📦 Добро пожаловать в [Postlink]! 📦
Этот бот помогает отправителям находить доставщиков, а доставщикам — зарабатывать на перевозке посылок.

🔹 Как это работает?
 
1️⃣ Отправитель создаёт заявку с описанием посылки и маршрутом. 

2️⃣ Доставщик выбирает подходящий рейс и договаривается о передаче. 

3️⃣ После доставки отправитель подтверждает получение, и сделка завершается.


⚠ Важно!

-Запрещена передача нелегальных товаров.

-Участники сами договариваются об оплате.
                         
-Бот не несёт ответственности за посылки и споры между пользователями.


🚀 Готовы начать? Нажмите "start" и создайте свою первую заявку!
''', reply_markup=kb.start_reply_mu)

async def after_auth(message: Message, state: FSMContext):
    await state.set_state(AppState.menu)
    await message.answer('Вы успешно авторизовались')
    await menu(message, state)

@router.message(AppState.initial, or_f(F.text.lower() == 'логин', Command('login')))
async def login(message: Message, state: FSMContext):
    await state.set_state(LoginState.phone)
    await message.answer('Напишите ваш сотовый номер телефона', reply_markup=kb.phone_reply_mu)

    
@router.message(LoginState.phone)
async def handle_phone(message: Message, state: FSMContext):
    
    if not message.contact:
        await message.reply('Можно узнать Ваш сотовый номер телефона?', reply_markup=kb.phone_reply_mu)
        return
    
    user_phone = message.contact.phone_number
    
    if not user_phone.startswith('+'):
        user_phone = '+' + user_phone
    
    await state.update_data(phone=user_phone)
    
    user = crud.get_user_by_phone(db, user_phone)
    if not user:
        await message.reply('Пользователя с таким номером телефона не найден, попробуйте зарегистрироваться')
        await state.set_state({}) 
        await back_to_start(message, state)
        return
    
    response = await context.otp_service.send_otp(user_phone)
    if 'message' in response:
        await message.reply('Сообщите 6 значный код отправленный вам на WhatsApp: ' + user_phone, reply_markup=ReplyKeyboardRemove())
        await state.update_data(phone=user_phone)
        await state.set_state(LoginState.otp_code)
    else:
        await message.reply('Попробуйте еще раз')
        await state.set_state(LoginState.phone)
        return

@router.message(LoginState.otp_code, F.text.len() != 6)
async def handle_invalid_otp_code(message: Message, state: FSMContext):
    await message.reply('Это не похоже на 6 значный код, попробуйте еще раз')
    await state.set_state(LoginState.otp_code)

@router.message(LoginState.otp_code, F.text.len() == 6, F.text.func(str.isdigit))
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
        user = crud.get_user_by_phone(db, phone)
        crud.add_user_telegram(db, user.id, message.from_user.id, message.from_user.username)
        
        await state.clear()
        await after_auth(message, state)
    else:
        await message.reply('Ошибка при обработке OTP. Попробуйте позже.')


@router.message(AppState.initial, or_f(F.text.lower() == 'регистрация', Command('register')))   
async def registration(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.name)
    await message.reply('Как Вас зовут?', reply_markup=kb.auth_back_reply_mu)

@router.message(StateFilter(RegistrationState), F.text == 'Назад')
async def back_to_start(message: Message, state: FSMContext):
    await state.set_state({})
    await state.set_state(AppState.initial)
    await message.answer('Выберите пожалуйста ниже что вас интересует', reply_markup=kb.start_reply_mu)


@router.message(RegistrationState.name)
@router.message(RegistrationState.city_confirmation, F.text.lower() == 'нет')
async def handle_name(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.city)

    if message.text.lower() == 'нет':
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)

    data = await state.get_data()
    name = data.get('name', message.text)
    await state.update_data(name=name)

    text = f'{name}, В каком городе Вы находитесь?'

    if('try_count' in data):
        text += '\nЕсли не можете найти, можно указать страну с городом.\nКазахстан, Алматы'
    await message.answer(text, reply_markup=kb.auth_back_reply_mu)
    
@router.message(RegistrationState.city)
async def handle_city(message: Message, state: FSMContext):
    
    service_response = await context.places_api.search_text(message.text)
    
    place = None
    
    if 'places' in service_response:
        place = service_response['places'][0]
    
    if place:
        await state.set_state(RegistrationState.city_confirmation)
        await message.answer(f'Вы находитесь в городе: {place["formattedAddress"]}?', reply_markup=kb.city_conf_reply_mu)    
        await state.update_data(city=place["formattedAddress"])
    else:
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)

        await message.answer('Город не найден. Попробуйте еще раз')

    
@router.message(RegistrationState.city_confirmation, F.text.lower() == 'да')
async def handle_city_confirmation(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.phone)
    await message.answer('Можно узнать Ваш сотовый номер телефона?', reply_markup=kb.phone_reply_mu)
    
    
@router.message(RegistrationState.phone)
async def handle_phone(message: Message, state: FSMContext):
    
    if not message.contact:
        await message.reply('Можно узнать Ваш сотовый номер телефона?', reply_markup=kb.phone_reply_mu)
        return
    
    user_phone = message.contact.phone_number
    
    if not user_phone.startswith('+'):
        user_phone = '+' + user_phone
    
    await state.update_data(phone=user_phone)
        
    if crud.is_user_phone_exists(db, user_phone):
        await message.reply('Пользователь с таким номером телефона уже существует, попробуйте войти')
        await state.set_state({})
        await back_to_start(message, state)
        return
    
    # Sending OTP
    response = await context.otp_service.send_otp(user_phone)
    if 'message' in response:
        await message.reply('Сообщите 6 значный код отправленный вам на WhatsApp: ' + user_phone, reply_markup=ReplyKeyboardRemove())
        await state.update_data(phone=user_phone)
        await state.set_state(RegistrationState.otp_code)
    else:
        await message.reply('Попробуйте еще раз')
        await state.set_state(RegistrationState.phone)
        return
    
@router.message(RegistrationState.otp_code, F.text.len() != 6)
async def handle_invalid_otp_code(message: Message, state: FSMContext):
    await message.reply('Это не похоже на 6 значный код, попробуйте еще раз')
    await state.set_state(RegistrationState.otp_code)

@router.message(RegistrationState.otp_code, F.text.len() == 6, F.text.func(str.isdigit))
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
            crud.create_user(
                db, tg_id=message.from_user.id, username=message.from_user.username,
                name=data['name'], phone=data['phone'], city=data['city']
            )
        except Exception as e:
            await message.reply('Ошибка при регистрации пользователя')
            await back_to_start(message, state)
            return

        await state.clear()
        await after_auth(message, state)
    else:
        await message.reply('Ошибка при обработке OTP. Попробуйте позже.')