from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import F

from src.database import db
from src.database.models import crud
from src.common.states import SupportState
from src.handlers import menu
from src.services import supp_request_sender as supp_serv


from src.common import keyboard as kb
from src.handlers.support import router
from .filters import KnownProblemFilter


@router.message(SupportState.user_type, F.text.lower().in_(['отправитель', 'курьер', 'новый пользователь']))
async def handle_user_type(message: Message, state: FSMContext):
    await state.update_data(user_type=message.text.lower())
    await message.answer('Что случилось?⬇️', reply_markup=kb.support_problems_reply_mu)
    await state.set_state(SupportState.problem)
    
@router.message(SupportState.problem, KnownProblemFilter())
async def handle_known_problem(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, расскажите нам про свою проблему.', reply_markup=ReplyKeyboardRemove())
    await state.set_state(SupportState.problem_description)
    
@router.message(SupportState.problem)
async def handle_unknown_problem(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, выберите наиболее подходящую ситуацию из списка ниже.', reply_markup=kb.support_problems_reply_mu)
    
@router.message(SupportState.user_type, F.text.lower() == 'назад')
async def back_to_menu(message: Message, state: FSMContext):
    await menu.handle_menu(message, state)

@router.message(SupportState.problem_description)
async def handle_other_problem_description(message: Message, state: FSMContext):
    await state.update_data(problem_description=message.text)
    await message.answer('Укажите номер заявки, по которому возникла проблема\n(Номер заявки можно найти в сообщении, подтверждающем создание заявки)', reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Проблема не связана с какой-либо из заявок')]], resize_keyboard=True))
    await state.set_state(SupportState.request_no)
    

@router.message(SupportState.request_no, F.text.func(str.isdigit))
async def handle_request_no(message: Message, state: FSMContext):
    await state.update_data(request_no=message.text)
    
    state_data = await state.get_data()
    user_type = state_data['user_type']
    request_data = None
    
    if user_type == 'отправитель':
        request_data = crud.get_send_request_by_id(db, message.text)
    else:
        request_data = crud.get_delivery_request_by_id(db, message.text)
        
    if not request_data:
        await message.answer('Заявка с таким номером не найдена. Пожалуйста, проверьте номер заявки и попробуйте еще раз', reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Проблема не связана с какой-либо из заявок')]], resize_keyboard=True))
        return
    
    await message.answer(f'''У вас возникла проблема по данной заявке?\nДетали заявки:\nСтатус вашей заявки: {request_data.status}\nНомер заявки: {request_data.id}\nГород отправления: {request_data.from_location}\nГород назначения: {request_data.to_location}\nДата отправления: c {request_data.from_date} по {request_data.to_date}\nВес и габариты: {request_data.size_type}\nДополнительные требования: {request_data.description}''', reply_markup=kb.confirmation_reply_mu)
    await state.set_state(SupportState.confirmation)
    
@router.message(SupportState.request_no, F.text.lower() == 'проблема не связана с какой-либо из заявок')
async def handle_no_request_related_problem(message: Message, state: FSMContext):
    await state.update_data(request_no=None)
    await handle_confirmation(message, state)

@router.message(SupportState.request_no)
async def handle_invalid_request_no(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, введите номер заявки в числовом формате')
    
@router.message(SupportState.confirmation, F.text.lower().in_(['да', 'нет']))
async def handle_confirmation(message: Message, state: FSMContext):
    if message.text.lower() == 'нет':
        await message.answer('Прошу перепроверить номер заявки, по которому у Вас возникла проблема и повторно отправить.', reply_markup=ReplyKeyboardRemove())
        await state.set_state(SupportState.request_no)
        return
    
    state_data = await state.get_data()
    
    support_request = crud.create_supp_request(db, message.from_user.id, state_data['problem_description'], state_data['user_type'], state_data['request_no'])
    await supp_serv.send_supp_request(support_request)
    
    await message.answer('✅ Спасибо! Мы получили вашу заявку и свяжемся с вами в ближайшее время.')
    await menu.handle_menu(message, state)