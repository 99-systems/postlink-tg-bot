from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, or_f, StateFilter
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery

from src.common.states import RegistrationState
import src.context as context


from src.common.states import AppState, SendParcelState
from src.common import keyboard as kb

from src.database.models import crud

from src.database.connection import db

router = Router()

from datetime import datetime

def is_valid_date_range(date_range: str) -> bool:
    try:
        start, end = date_range.split('-')
        start = datetime.strptime(start.strip(), "%d.%m.%Y")
        end = datetime.strptime(end.strip(), "%d.%m.%Y")
        return start <= end  # Дата начала не должна быть позже даты конца
    except ValueError:
        return False


@router.message(SendParcelState.from_city_confirmation, F.text.lower() == 'нет')
@router.message(AppState.menu, or_f(F.text.lower() == 'отправить посылку', Command('/send_parcel')))
async def send_parcel(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.from_city)
    if message.text.lower() == 'нет':
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)
    data = await state.get_data()

    if('try_count' in data):
        await message.answer('Откуда вы отправляетесь?\nЕсли не можете найти, можно указать страну с городом.\nКазахстан, Алматы')
    await message.answer('Откуда вы отправляетесь?', reply_markup=kb.create_from_curr_city_mu(curr_city))

@router.callback_query(SendParcelState.from_city, F.data == 'from_city:current')
async def from_city_kb(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SendParcelState.to_city)
    curr_city = crud.get_city_by_tg_id(db, callback.from_user.id)
    await callback.answer('')
    await to_city(callback.message, state, callback.from_user)
    return


@router.message(SendParcelState.from_city)
async def from_city(message: Message, state: FSMContext):
    
    service_response = await context.places_api.search_text(message.text)
    
    place = None
    
    if 'places' in service_response:
        place = service_response['places'][0]
    
    if place:
        await state.set_state(SendParcelState.from_city_confirmation)
        await message.answer(f'Отправляетесь отсюда?: {place["formattedAddress"]}?', reply_markup=kb.city_conf_reply_mu)    
        await state.update_data(from_city=place["formattedAddress"])
    else:
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)

        await message.answer('Город не найден. Попробуйте еще раз')






@router.message(SendParcelState.from_city_confirmation, F.text.lower() == 'да')
@router.message(SendParcelState.to_city_confirmation, F.text.lower() == 'нет')
async def to_city(message: Message, state: FSMContext, user = None):
    if await state.get_state() == SendParcelState.from_city_confirmation:
        await state.update_data(try_count=0)
    elif await state.get_state() == SendParcelState.to_city_confirmation:
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
    await state.set_state(SendParcelState.to_city)
    data = await state.get_data()

    user = user or message.from_user
    curr_city = crud.get_city_by_tg_id(db, user.id)
    
    if('try_count' in data) and data['try_count'] > 0:
        await message.answer('Куда вы отправляетесь?\nЕсли не можете найти, можно указать страну с городом.\nКазахстан, Алматы', reply_markup=kb.create_from_curr_city_mu(curr_city))
    await message.answer('Куда вы отправляетесь?', reply_markup=kb.create_from_curr_city_mu(curr_city))

@router.callback_query(SendParcelState.to_city, F.data == 'to_city:current')
async def to_city_kb(callback: CallbackQuery, state: FSMContext):
    curr_city = crud.get_city_by_tg_id(db, callback.from_user.id)
    await callback.answer('')

    await date_choose(callback.message, state, callback.from_user)
    return


@router.message(SendParcelState.to_city)
async def to_city_confirmation(message: Message, state: FSMContext):
    
    service_response = await context.places_api.search_text(message.text)
    
    place = None
    
    if 'places' in service_response:
        place = service_response['places'][0]
    
    if place:
        await state.set_state(SendParcelState.to_city_confirmation)
        await message.answer(f'Отправляетесь сюда?: {place["formattedAddress"]}?', reply_markup=kb.city_conf_reply_mu)    
        await state.update_data(to_city=place["formattedAddress"])
    else:
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)

        await message.answer('Город не найден. Попробуйте еще раз')

      
@router.message(SendParcelState.date_confirmation, F.text.lower() == 'нет')
@router.message(SendParcelState.to_city_confirmation, F.text.lower() == 'да')
async def date_choose(message: Message, state: FSMContext, user = None):
    await state.set_state(SendParcelState.date_choose)
    await message.answer('Напишите в какие числа вам желательно отправить посылку.\nВ таком формате: 10.02.2025 - 02.03.2025')


@router.message(SendParcelState.date_choose)
async def date_confirmation(message: Message, state: FSMContext):
    start, end = message.text.split('-')
    start = start.strip()
    end = end.strip()  

    if is_valid_date_range(message.text):
        await state.set_state(SendParcelState.date_confirmation)
        await message.answer(f'Вы хотите отправить посылку с {start} по {end}?', reply_markup=kb.city_conf_reply_mu)
    else:
        await message.answer('Неверный формат даты. Попробуйте еще раз в таком формате: 10.02.2025 - 02.03.2025')


@router.message(SendParcelState.date_confirmation, F.text.lower() == 'да')
async def size_choose(message: Message, state: FSMContext):
    await message.answer('Какой вес и габариты посылки?', reply_markup=kb.sizes_kb)
    await state.set_state(SendParcelState.size_confirmation)

@router.callback_query(SendParcelState.size_confirmation, F.data.startswith('size:'))
async def size_kb(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Напишите дополнительные требования или примечания к доставке', reply_markup=kb.no_desc_kb)
    await state.set_state(SendParcelState.description)


@router.message(SendParcelState.description)
async def desc_text(message: Message, state: FSMContext):
    await message.answer('Отлично, ваша заявка создана!\nВот ваша заявка: ')

@router.callback_query(SendParcelState.description, F.data == 'no_desc')
async def no_desc(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Отлично, ваша заявка создана!\nВот ваша заявка: ')

