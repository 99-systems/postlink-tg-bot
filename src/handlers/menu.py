from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery


from src.database.models import crud
from src.database.connection import db

from src.common.states import AppState, SupportState
from src.handlers.support import support_problems
from src.common import keyboard as kb

router = Router()



# TODO: Set AppState.menu after authorization
# Currently it's set with /menu command
@router.message(or_f(F.text.lower() == 'меню', Command('menu')))
async def set_state_menu(message: Message, state: FSMContext):
    await state.set_state(AppState.menu)
    await message.reply('Сейчас можно работать с меню')


@router.message(F.text.lower() == 'служба поддержки', AppState.menu)
async def handle_support(message: Message, state: FSMContext):
    
    keyboard = [[KeyboardButton(text=problem.name)] for problem in support_problems] + [[KeyboardButton(text='Другое')]]
    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await state.set_state(SupportState.initial)
    
    await message.answer('Опишите проблему', reply_markup=reply_markup)
    

@router.message(F.text.lower() == 'отправить посылку', AppState.menu)
async def send_parcel(message: Message, state: FSMContext):
    await message.answer('Отправка посылки в разработке')
    
@router.message(F.text.lower() == 'доставить посылку', AppState.menu)
async def deliver_parcel(message: Message, state: FSMContext):
    await message.answer('Доставка посылки в разработке')
    
    
@router.message(or_f(F.text.lower() == 'выход', Command('exit')))
async def exit(message: Message, state: FSMContext):
    try:
        exit_user = crud.delete_user_telegram(db, tg_id=message.from_user.id)
    except Exception as e:
        await message.answer('Ошибка при выходе из системы')
        print(e)
        return
    await message.answer('Вы вышли из аккаунта', reply_markup=kb.start_reply_mu)
    await state.set_state(AppState.initial)

    
@router.message(AppState.menu)
async def menu(message: Message, state: FSMContext):
    await message.reply('Что вас интересует?', reply_markup=kb.main_menu_reply_mu)
    await state.set_state(AppState.menu)



