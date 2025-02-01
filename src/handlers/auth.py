from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.common.states import RegistrationState

router = Router()


@router.message(Command('login'))
async def login(message: Message, state: FSMContext):
    await message.answer('This is login')
    

@router.message(RegistrationState.name)
async def handle_name(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.city)
    
    await message.answer('В каком городе Вы находитесь?')
    
@router.message(RegistrationState.city)
async def handle_city(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.phone)
    
    keyboard = [[KeyboardButton(text='Отправить номер телефона', request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await message.answer('Можно узнать Ваш сотовый номер телефона?', reply_markup=reply_markup)
    
@router.message(RegistrationState.phone)
async def handle_phone(message: Message, state: FSMContext):
    await message.reply('Сообщите 3-х значный код отправленный вам на WhatsApp', reply_markup=ReplyKeyboardRemove())