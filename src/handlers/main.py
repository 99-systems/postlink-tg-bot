from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from src.common.states import SupportState
from src.common import keyboard as kb

router = Router()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.answer('Приступим к работе!')




@router.message(F.text.lower() == 'служба поддержки')
async def handle_support(message: Message, state: FSMContext):
    await message.answer(
        'Привет! Это служба поддержки PostLink.\nПожалуйста, ответьте на несколько вопросов, и мы сделаем все, что в наших силах!',
        reply_markup=ReplyKeyboardRemove())
    await message.answer('Выберите, кто Вы сейчас⬇️', reply_markup=kb.user_type_reply_mu)
    await state.set_state(SupportState.user_type)