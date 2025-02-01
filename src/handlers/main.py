from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from src.common.states import AppState, RegistrationState, LoginState

router = Router()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    
    await state.set_state(AppState.initial)
    
    keyboard = [[KeyboardButton(text='Регистрация')], [KeyboardButton(text='Логин')]]
    reply_makrup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await message.answer('Приветствую! Выберите пожалуйста ниже что вас интересует', reply_markup=reply_makrup)


@router.message(AppState.initial, F.text=='Регистрация')   
async def registration(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.name)
    
    await message.reply('Как Вас зовут?')

@router.message(AppState.initial, F.text=='Логин')
async def login(message: Message, state: FSMContext):
    await message.reply('Сработал логин')