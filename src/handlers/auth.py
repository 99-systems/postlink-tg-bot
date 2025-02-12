from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, or_f, StateFilter
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.common.states import RegistrationState
import src.context as context


from src.common.states import AppState, RegistrationState, LoginState
from src.common import keyboard as kb

from src.database.models import crud

from src.database.connection import db

router = Router()

# TODO: Ошибка с хранением данных в состоянии FSM



@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(AppState.initial)
    await message.answer('Приветствую! Выберите пожалуйста ниже что вас интересует', reply_markup=kb.start_reply_mu)

async def after_auth(message: Message, state: FSMContext):
    await state.set_state(AppState.menu)
    await message.answer('Вы успешно авторизовались')
    await message.answer('Что вас интересует?', reply_markup=kb.main_menu_reply_mu)
    await state.set_state(AppState.menu)

@router.message(AppState.initial, or_f(F.text.lower() == 'логин', Command('login')))
async def login(message: Message, state: FSMContext):
    await state.set_state(LoginState.phone)
    await message.answer('Напишите ваш сотовый номер телефона', reply_markup=kb.phone_reply_mu)

    
@router.message(LoginState.phone)
async def handle_phone(message: Message, state: FSMContext):
    await state.update_data(phone =  message.contact.phone_number)
    data = await state.get_data()  
    user = crud.get_user_by_phone(db, data['phone'])
    if not user:
        await message.reply('Пользователя с таким номером телефона не найден, попробуйте зарегистрироваться')
        await state.set_state({}) 
        await back_to_start(message, state)
        return
    
    
    await message.reply('Сообщите 3-х значный код отправленный вам на WhatsApp' + data['phone'], reply_markup=ReplyKeyboardRemove())
    
    try: 
        create_tg_user = crud.add_user_telegram(db, tg_id=message.from_user.id, username=message.from_user.username, user_id=user.id)
    except Exception as e:
        await message.reply('Ошибка при добавлении пользователя')
        print(e)
        await back_to_start(message, state)
        return

    await after_auth(message, state)

    

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
    await message.reply('Сообщите 3-х значный код отправленный вам на WhatsApp' + message.contact.phone_number, reply_markup=ReplyKeyboardRemove())
    
    await state.update_data(phone =  message.contact.phone_number)
    
    data = await state.get_data()
    await message.reply(data['name'] + ' ' + data['city'] + ' ' + data['phone'])
    

    if crud.is_user_phone_exists(db, data['phone']):
        await message.reply('Пользователь с таким номером телефона уже существует, попробуйте войти')
        await state.set_state({})
        await back_to_start(message, state)
        return

    try:
        user = crud.create_user(
            db, tg_id=message.from_user.id, username=message.from_user.username,
            name=data['name'], phone=data['phone'], city=data['city']
            )
    except Exception as e:
        await message.reply('Ошибка при регистрации пользователя')
        print(e)
        await back_to_start(message, state)
        return
    
    await state.set_state({})

    await message.reply(f'Пользователь {user.name} успешно добавлен')

    await after_auth(message, state)
