from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, or_f, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters.command import CommandObject

from src.database.models import crud
from src.database import db

from src.common.states import AppState, SupportState
from src.common import keyboard as kb
from typing import Optional

router = Router()

@router.message(AppState.menu, CommandStart())
@router.message(or_f(F.text.lower() == 'меню', Command('menu')))
async def handle_menu(message: Message, state: FSMContext, command: Optional[CommandObject] = None):
    if command.args == "support":
        await message.answer('Привет! Это служба поддержки PostLink.\nПожалуйста, ответьте на несколько вопросов, и мы сделаем все, что в наших силах!', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите, кто Вы сейчас⬇️', reply_markup=kb.user_type_reply_mu)
        await state.set_state(SupportState.user_type)
        return
    
    await state.set_state(AppState.menu)
    state_data = await state.get_data()
    tg_user_id = state_data.get('tg_user_id', message.from_user.id)
    
    await message.answer('Что вас интересует из перечисленного?', reply_markup=kb.create_main_menu_markup(tg_user_id))

@router.message(CommandStart())
async def start(message: Message, state: FSMContext, command: Optional[CommandObject] = None):
    print(message.from_user)
    if command.args == "support":
        await message.answer('Привет! Это служба поддержки PostLink.\nПожалуйста, ответьте на несколько вопросов, и мы сделаем все, что в наших силах!', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите, кто Вы сейчас⬇️', reply_markup=kb.user_type_reply_mu)
        await state.set_state(SupportState.user_type)
        return

SECURITY_LINKS = {
    "безопасность отправителей": "https://telegra.ph/CHek-list-dlya-otpravitelej-PostLink-03-12",
    "безопасность курьеров": "https://telegra.ph/CHek-list-dlya-kurerov-PostLink-03-12",
}

@router.message(F.text.lower().in_(SECURITY_LINKS), AppState.menu)
async def security_info(message: Message, state: FSMContext):
    link = SECURITY_LINKS[message.text.lower()]
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Читать", url=link)]]
    )

    await message.answer(
        "<b>PostLink</b> заботится о безопасности своих пользователей. Пожалуйста, ознакомьтесь с рекомендациями, которые помогут избежать рисков и недоразумений.",
        reply_markup=reply_markup, parse_mode='HTML'
    )


    
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