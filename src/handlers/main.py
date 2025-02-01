from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.answer('Hello!')