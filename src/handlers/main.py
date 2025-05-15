from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters.command import CommandObject


import src.database.models.crud as crud
from src.common.states import AppState, SupportState, RegistrationState, LoginState
from src.common import keyboard as kb
from src.database import db
from typing import Optional


router = Router()


@router.message(StateFilter(None, AppState.auth), CommandStart())
async def start(message: Message, state: FSMContext, command: Optional[CommandObject] = None):
    print(message.from_user)
    if command.args == "support":
        await handle_support(message, state)
    
    await state.update_data(tg_user_id=message.from_user.id)
    
    tg_user = crud.get_tg_user(db, message.from_user.id)
    if not tg_user:
        tg_user = crud.add_tg_user(db, message.from_user.id, message.from_user.username)

    await state.set_state(AppState.menu)  
    state_data = await state.get_data()
    tg_user_id = state_data.get('tg_user_id', message.from_user.id)
    
    await message.answer('Что вас интересует из перечисленного?', reply_markup=kb.create_main_menu_markup(tg_user_id))



# @router.message(RegistrationState.name, F.text.lower() == 'назад')
# @router.message(LoginState.phone, F.text.lower() == 'назад')
async def handle_start(message: Message, state: FSMContext):
    await state.set_state(AppState.menu)
    state_data = await state.get_data()
    tg_user_id = state_data.get('tg_user_id', message.from_user.id)
    
    await message.answer('Что вас интересует из перечисленного?', reply_markup=kb.create_main_menu_markup(tg_user_id))


@router.message(F.text.lower() == 'служба поддержки', AppState.menu)
async def handle_support(message: Message, state: FSMContext):
    
    await message.answer('Привет! Это служба поддержки PostLink.\nПожалуйста, ответьте на несколько вопросов, и мы сделаем все, что в наших силах!', reply_markup=ReplyKeyboardRemove())
    await message.answer('Выберите, кто Вы сейчас⬇️', reply_markup=kb.user_type_reply_mu)
    await state.set_state(SupportState.user_type)