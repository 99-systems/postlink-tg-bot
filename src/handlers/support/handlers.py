from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.models import crud
from src.common.states import SupportState
from src.handlers import menu
from src.services import supp_request_sender as supp_serv


from src.handlers.support import router
from .filters import KnownProblemFilter, UnkownProblemFilter

@router.message(SupportState.initial, UnkownProblemFilter(), F.text.lower() == 'другое')
async def handle_other_problem(message: Message, state: FSMContext):
    await state.set_state(SupportState.unknown_problem_description)
    await message.answer('Опишите проблему подробнее', reply_markup=ReplyKeyboardRemove())
    
@router.message(SupportState.initial, KnownProblemFilter())
async def handle_known_problem(message: Message, state: FSMContext):
    req = crud.create_supp_request(db, message.from_user.id, message.text)
    await supp_serv.send_supp_request(req)
    await message.answer(f'В ближайшее время мы свяжемся с Вами для уточнения деталей. Просим ожидать звонка. Номер вашей заявки: {req.id}', reply_markup=ReplyKeyboardRemove())
    await menu.handle_menu(message, state)
    
@router.message(SupportState.initial, F.text.lower() == 'назад')
async def back_to_menu(message: Message, state: FSMContext):
    await menu.handle_menu(message, state)

@router.message(SupportState.unknown_problem_description)
async def handle_other_problem_description(message: Message, state: FSMContext):
    req = crud.create_supp_request(db, message.from_user.id, message.text)
    await supp_serv.send_supp_request(req)
    await message.answer(f'В ближайшее время мы свяжемся с Вами для уточнения деталей. Просим ожидать звонка. Номер вашей заявки: {req.id}', reply_markup=ReplyKeyboardRemove())
    await menu.handle_menu(message, state)