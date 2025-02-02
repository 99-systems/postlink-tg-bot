from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from src.common.states import AppState, RegistrationState
from src.common import keyboard as kb


router = Router()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(AppState.initial)
    await message.answer('Приветствую! Выберите пожалуйста ниже что вас интересует', reply_markup=kb.start_reply_mu)