from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.common.states import SupportState
from src.common import keyboard as kb

router = Router()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    simple_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Служба поддержки')]],
        resize_keyboard=True
    )
    # --- Inline keyboard for the web-app button ---
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='Открыть PostLink',
            web_app={'url': 'https://backend.sdutalks.kz'}
        )
    )
    inline_kb = builder.as_markup()
    # ---------------------------------------------
    welcome_message = (
        "Добро пожаловать в <b>PostLink</b> 👋\n\n"
        "PostLink — это сервис, который соединяет отправителей и путешественников.\n"
        "📦 <b>Отправителю</b> — быстрый и удобный способ передать посылку.\n"
        "✈️ <b>Путешественнику</b> — возможность заработать в пути.\n\n"
        "<blockquote><b>Как это работает:</b>\n"
        "1️⃣ Выбираешь направление\n"
        "2️⃣ Создаёшь заявку или откликаешься на чужую\n"
        "3️⃣ Получаешь отклик и договариваешься в чате</blockquote>\n\n"
        "🚀 Всё просто: открой приложение и проверь всё сам 👇🏻"
    )

    await message.answer(welcome_message, reply_markup=simple_kb, parse_mode="HTML")
    await message.answer(
        "👆🏻 Нажмите кнопку ниже, чтобы открыть PostLink:",
        reply_markup=inline_kb           # InlineKeyboardMarkup
    )



@router.message(Command("support"))
@router.message(F.text.in_(['Служба поддержки', 'служба поддержки', 'СЛУЖБА ПОДДЕРЖКИ']))
async def handle_support(message: Message, state: FSMContext):
    print(f"Support handler triggered by: '{message.text}' from user {message.from_user.id}")
    await message.answer(
        'Привет! Это служба поддержки PostLink.\nПожалуйста, ответьте на несколько вопросов, и мы сделаем все, что в наших силах!',
        reply_markup=ReplyKeyboardRemove())
    await message.answer('Выберите, кто Вы сейчас⬇️', reply_markup=kb.user_type_reply_mu)
    await state.set_state(SupportState.user_type)

@router.callback_query(F.data == 'support_start')
async def handle_support_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        'Привет! Это служба поддержки PostLink.\nПожалуйста, ответьте на несколько вопросов, и мы сделаем все, что в наших силах!',
        reply_markup=ReplyKeyboardRemove())
    await callback.message.answer('Выберите, кто Вы сейчас⬇️', reply_markup=kb.user_type_reply_mu)
    await state.set_state(SupportState.user_type)

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message, state: FSMContext):
    try:
        import json
        data = json.loads(message.web_app_data.data)
        
        if data.get('action') == 'support_request':
            await handle_support(message, state)
        
    except Exception as e:
        print(f"Error handling web app data: {e}")
        await message.answer("Произошла ошибка при обработке запроса")