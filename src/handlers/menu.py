from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton


from src.database.models import crud
from src.database import db

from src.common.states import AppState, SupportState
from src.common import keyboard as kb

from .support import support_problems


router = Router()

@router.message(AppState.menu, Command('start'))
@router.message(or_f(F.text.lower() == 'меню', Command('menu')))
async def handle_menu(message: Message, state: FSMContext):
    await state.set_state(AppState.menu)
    reply_markup = (kb.main_menu_open_req_reply_mu 
                    if crud.is_open_request_by_tg_id(db, message.from_user.id) 
                    else kb.main_menu_reply_mu)

    await message.answer('Что вас интересует из перечисленного?', reply_markup=reply_markup)


@router.message(F.text.lower() == 'краткая инструкция', AppState.menu)
async def instruction(message: Message, state: FSMContext):
    await message.answer('Тут будет Инструкция', reply_markup=kb.main_menu_reply_mu)


@router.message(F.text.lower() == 'служба поддержки', AppState.menu)
async def handle_support(message: Message, state: FSMContext):
    
    keyboard = [[KeyboardButton(text=problem.name)] for problem in support_problems] + [[KeyboardButton(text='Другое')]] + [[KeyboardButton(text='Назад')]]
    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await state.set_state(SupportState.initial)
    await message.answer('Опишите проблему', reply_markup=reply_markup)
    
    
@router.message(or_f(F.text.lower() == 'выход', Command('exit')), AppState.menu)
async def exit(message: Message, state: FSMContext):
    try:
        user = crud.get_user_by_tg_id(db, message.from_user.id)
        crud.delete_session(db, user.id)
    except Exception as e:
        await message.answer('Ошибка при выходе из системы')
        print(e)
        return
    await message.answer('Вы вышли из аккаунта', reply_markup=kb.auth_reply_mu)
    await state.set_state(AppState.auth)