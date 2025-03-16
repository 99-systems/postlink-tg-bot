from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import F


from src.handlers.menu import handle_menu
from src.handlers.main import handle_start
from src.common.states import RegistrationState

from src.handlers.auth import router



async def handle_success_auth(message: Message, state: FSMContext):
    await message.answer('Вы успешно авторизовались.\nНадеюсь, я решу поставленную цель!')
    await handle_menu(message, state)
    
    
@router.message(RegistrationState.name, F.text.lower() == 'назад')
async def handle_back_start(message: Message, state: FSMContext):
    await handle_start(message, state)