import logging
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import F

from src.database.connection import get_db
from src.database.models import crud
from src.database.models.request import SendRequest
from src.common.states import SupportState
from src.services import supp_request_sender as supp_serv


from src.common import keyboard as kb
from src.handlers.support import router
from .filters import KnownProblemFilter

logging.basicConfig(level=logging.INFO)


@router.message(SupportState.user_type, F.text.lower().in_(['отправитель', 'курьер', 'новый пользователь']))
async def handle_user_type(message: Message, state: FSMContext):
    logging.info(f"User {message.from_user.id} selected user type: {message.text.lower()}")
    await state.update_data(user_type=message.text.lower())
    await message.answer('Что случилось?⬇️', reply_markup=kb.support_problems_reply_mu)
    await state.set_state(SupportState.problem)
    
@router.message(SupportState.problem, KnownProblemFilter())
async def handle_known_problem(message: Message, state: FSMContext):
    logging.info(f"User {message.from_user.id} selected known problem: {message.text}")
    await message.answer('Пожалуйста, расскажите нам про свою проблему.', reply_markup=ReplyKeyboardRemove())
    await state.set_state(SupportState.problem_description)
    
@router.message(SupportState.problem)
async def handle_unknown_problem(message: Message, state: FSMContext):
    logging.warning(f"User {message.from_user.id} selected an unknown problem: {message.text}")
    await message.answer('Пожалуйста, выберите наиболее подходящую ситуацию из списка ниже.', reply_markup=kb.support_problems_reply_mu)
    
@router.message(SupportState.user_type, F.text.lower() == 'назад')
async def back_to_menu(message: Message, state: FSMContext):
    logging.info(f"User {message.from_user.id} went back to the main menu.")
    simple_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Служба поддержки')]],
        resize_keyboard=True
    )
    await message.answer('Главное меню', reply_markup=simple_kb)
    await state.clear()

@router.message(SupportState.problem_description)
async def handle_other_problem_description(message: Message, state: FSMContext):
    logging.info(f"User {message.from_user.id} provided problem description: {message.text}")
    await state.update_data(problem_description=message.text)

    state_data = await state.get_data()

    await message.answer(
        '✅ Спасибо! Мы получили вашу заявку и свяжемся с вами в ближайшее время.',
        reply_markup=ReplyKeyboardRemove()
    )
    try:
        logging.info(f"Creating support request for user {message.from_user.id} with data: {state_data}")
        with get_db() as db:
            support_request = crud.create_supp_request(
                db,
                message.from_user.id,
                state_data['problem_description'],
                state_data['user_type'],
            )
            logging.info(f"Support request {support_request.id} created successfully.")
            await supp_serv.send_supp_request(support_request.id)
    except Exception as e:
        logging.error(f"Error creating or sending support request for user {message.from_user.id}: {e}")

    simple_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Служба поддержки')]],
        resize_keyboard=True
    )
    await message.answer('Главное меню', reply_markup=simple_kb)
    await state.clear()

    # await state.set_state(SupportState.confirmation)

#
# @router.message(SupportState.confirmation)
# async def handle_confirmation(message: Message, state: FSMContext):
#     state_data = await state.get_data()
#
#     support_request = crud.create_supp_request(
#         db,
#         message.from_user.id,
#         state_data['problem_description'],
#         state_data['user_type'],
#     )
#     await supp_serv.send_supp_request(support_request)
#
#     simple_kb = ReplyKeyboardMarkup(
#         keyboard=[[KeyboardButton(text='Служба поддержки')]],
#         resize_keyboard=True
#     )
#     await message.answer('Главное меню', reply_markup=simple_kb)
#     await state.clear()