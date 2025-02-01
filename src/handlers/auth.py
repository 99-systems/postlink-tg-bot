from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.common.states import RegistrationState
import src.context as context

router = Router()


@router.message(Command('login'))
async def login(message: Message, state: FSMContext):
    await message.answer('This is login')
    

@router.message(RegistrationState.name)
@router.message(RegistrationState.city_confirmation, F.text == 'Нет')
async def handle_name(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.city)
    
    await message.answer('В каком городе Вы находитесь?', reply_markup=ReplyKeyboardRemove())
    
@router.message(RegistrationState.city)
async def handle_city(message: Message, state: FSMContext):
    
    service_response = await context.places_api.search_text(message.text)
    
    place = None
    
    if 'places' in service_response:
        place = service_response['places'][0]
    
    if place:
        await state.set_state(RegistrationState.city_confirmation)

        reply_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]], resize_keyboard=True)
        await message.answer(f'Вы находитесь в городе: {place['formattedAddress']}?', reply_markup=reply_markup)
    
    else:
        await message.answer('Город не найден. Попробуйте еще раз')

    
@router.message(RegistrationState.city_confirmation, F.text == 'Да')
async def handle_city_confirmation(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.phone)
        
    keyboard = [[KeyboardButton(text='Отправить номер телефона', request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await message.answer('Можно узнать Ваш сотовый номер телефона?', reply_markup=reply_markup)
    
    
@router.message(RegistrationState.phone)
async def handle_phone(message: Message, state: FSMContext):
    await message.reply('Сообщите 3-х значный код отправленный вам на WhatsApp', reply_markup=ReplyKeyboardRemove())