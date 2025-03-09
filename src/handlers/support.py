from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Filter
from aiogram.types import Message, ReplyKeyboardRemove

from src.common.states import SupportState

from src.database.models import crud
from src.database.connection import db
from src.handlers import menu

from src.services import supp_request_sender as supp_serv

router = Router()



class SupportProblem:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def __str__(self):
        return self.name.lower()
    
    
support_problems = [
    SupportProblem(1, 'Не могу дозвониться до Курьера/Отправителя'),
    SupportProblem(2, 'Курьер отказался взять посылку'),
    SupportProblem(3, 'Посылка была утеряна в ходе доставки'),
]


class KnownProblemFilter(Filter):
    
    def __init__(self):
        self.problems = [str(problem) for problem in support_problems]
    
        
    async def __call__(self, message: Message):
        return message.text.lower() in self.problems
    
class UnkownProblemFilter(Filter):
    
    def __init__(self):
        self.problems = [str(problem) for problem in support_problems]
    
    async def __call__(self, message: Message):
        return message.text.lower() not in self.problems



@router.message(SupportState.initial, UnkownProblemFilter(), F.text.lower() == 'другое')
async def handle_other_problem(message: Message, state: FSMContext):
    await state.set_state(SupportState.unknown_problem_description)
    await message.answer('Опишите проблему подробнее', reply_markup=ReplyKeyboardRemove())
    
@router.message(SupportState.initial, KnownProblemFilter())
async def handle_known_problem(message: Message, state: FSMContext):
    req = crud.create_supp_request(db, message.from_user.id, message.text)
    await supp_serv.send_supp_request(req)
    await message.answer(f'В ближайшее время мы свяжемся с Вами для уточнения деталей. Просим ожидать звонка. Номер вашей заявки: {req.id}', reply_markup=ReplyKeyboardRemove())
    await menu.menu(message, state)
    
@router.message(SupportState.initial, F.text.lower() == 'назад')
async def back_to_menu(message: Message, state: FSMContext):
    await menu.menu(message, state)

@router.message(SupportState.unknown_problem_description)
async def handle_other_problem_description(message: Message, state: FSMContext):
    req = crud.create_supp_request(db, message.from_user.id, message.text)
    await supp_serv.send_supp_request(req)
    await message.answer(f'В ближайшее время мы свяжемся с Вами для уточнения деталей. Просим ожидать звонка. Номер вашей заявки: {req.id}', reply_markup=ReplyKeyboardRemove())
    await menu.menu(message, state)