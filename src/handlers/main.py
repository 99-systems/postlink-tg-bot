from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, FSInputFile


import src.database.models.crud as crud
from src.common.states import AppState
from src.common import keyboard as kb
from src.database import db


router = Router()

@router.message(StateFilter(None, AppState.auth), Command("start"))
async def start(message: Message, state: FSMContext):
    
    tg_user = crud.get_tg_user(db, message.from_user.id)
    
    if not tg_user:
        tg_user = crud.add_tg_user(db, message.from_user.id, message.from_user.username)
    
    if tg_user.accepted_terms:
        await handle_start(message, state)
    else:
        await message.answer('''
Важно знать!

❗ PostLink не участвует в доставке и не проверяет содержимое посылок.
Мы только находим и связываем нужные контакты за небольшую плату.
Вся ответственность за передачу и безопасность сделки лежит на самих пользователях.

‼️Перед началом работы ознакомьтесь с Пользовательским соглашением:
''')    
        await state.set_state(AppState.terms)
        await send_terms(message, state)
        
    
async def handle_start(message: Message, state: FSMContext):
    await message.answer('Еще раз Добро Пожаловать!', reply_markup=kb.auth_reply_mu)
    await state.set_state(AppState.auth)

@router.message(F.text.lower() == 'согласен', AppState.terms)
async def accept_terms(message: Message, state: FSMContext):
    crud.accept_terms(db, message.from_user.id)
    
    await handle_start(message, state)
    
@router.message(F.text.lower() == 'не согласен', AppState.terms)
async def decline_terms(message: Message, state: FSMContext):
    await state.set_state(AppState.terms_declined)
    await message.answer('К сожалению, без согласия с пользовательским соглашением, использование PostLink невозможно.\nПрошу еще раз ознакомиться с пользовательским соглашением и нажать "Согласен" для дальнейшего взаимодействия.', reply_markup=kb.open_terms_reply_mu)


@router.message(F.text.lower() == 'открыть пользовательское соглашение', AppState.terms_declined)
async def send_terms(message: Message, state: FSMContext):
    await state.set_state(AppState.terms)
    await message.answer_document(document=FSInputFile('src/files/user_agreement.pdf', 'Пользовательское соглашение.pdf'), caption='✅ Нажимая «Согласен», ты подтверждаешь, что ознакомился с условиями использования сервиса.', reply_markup=kb.terms_reply_mu)
    

@router.message(AppState.terms)
@router.message(AppState.terms_declined)
async def no_match(message: Message, state: FSMContext):
    
    current_state = await state.get_state()
    reply_markup = None
    
    if current_state == AppState.terms:
        reply_markup = kb.terms_reply_mu
    elif current_state == AppState.terms_declined:
        reply_markup = kb.open_terms_reply_mu
    
    await message.answer('Пожалуйста, воспользуйтесь кнопками.', reply_markup=reply_markup)