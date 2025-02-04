from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton


from src.common.states import AppState, SupportState
from src.handlers.support import support_problems


router = Router()



# TODO: Set AppState.menu after authorization
# Currently it's set with /menu command
@router.message(Command('menu'))
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
    
    
@router.message(AppState.menu)
async def menu(message: Message, state: FSMContext):
    
    
    keyboard = [[KeyboardButton(text='Отправить посылку')], [KeyboardButton(text='Доставить посылку')], [KeyboardButton(text='Служба поддержки')]]
    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await message.reply('Что вас интересует?', reply_markup=reply_markup)