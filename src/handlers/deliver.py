from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

import src.context as context


from src.common.states import AppState, DeliverParcelState
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


@router.message(DeliverParcelState.to_city_confirmation, F.text.lower() == 'нет')
@router.message(AppState.menu, or_f(F.text.lower() == 'доставить посылку', Command('/deliver_parcel')))
async def deliver_parcel(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.to_city)
    if message.text.lower() == 'нет':
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)
    data = await state.get_data()

    if 'try_count' in data:
        await message.answer('Куда доставить посылку?\nЕсли не можете найти, можно указать страну с городом.\nКазахстан, Алматы')
    await message.answer('Куда доставить посылку?', reply_markup=kb.create_from_curr_city_mu(curr_city))


@router.message(DeliverParcelState.to_city)
async def to_city(message: Message, state: FSMContext):
    service_response = await context.places_api.search_text(message.text)
    place = None
    if 'places' in service_response:
        place = service_response['places'][0]
    if place:
        await state.set_state(DeliverParcelState.to_city_confirmation)
        await message.answer(f'Доставить сюда?: {place["formattedAddress"]}?', reply_markup=kb.city_conf_reply_mu)
        await state.update_data(to_city=place["formattedAddress"])
    else:
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
        await message.answer('Город не найден. Попробуйте еще раз')


@router.message(DeliverParcelState.to_city_confirmation, F.text.lower() == 'да')
async def date_choose(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.date_choose)
    await message.answer('Укажите желаемые даты доставки в формате: 10.02.2025 - 02.03.2025')


@router.message(DeliverParcelState.date_choose)
async def date_confirmation(message: Message, state: FSMContext):
    try:
        start, end = message.text.split('-')
    except ValueError:
        await message.answer('Неверный формат даты. Попробуйте еще раз в таком формате: 10.02.2025 - 02.03.2025')
        return
    start = start.strip()
    end = end.strip()  

    if is_valid_date_range(message.text):
        await state.update_data(start_date=start, end_date=end)
        await state.set_state(DeliverParcelState.date_confirmation)
        await message.answer(f'Доставка в период с {start} по {end}?', reply_markup=kb.city_conf_reply_mu)
    else:
        await message.answer('Неверный формат даты. Попробуйте еще раз в таком формате: 10.02.2025 - 02.03.2025')


from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery

import src.context as context


from src.common.states import AppState, DeliverParcelState
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


@router.message(DeliverParcelState.to_city_confirmation, F.text.lower() == 'нет')
@router.message(AppState.menu, or_f(F.text.lower() == 'доставить посылку', Command('/deliver_parcel')))
async def deliver_parcel(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.to_city)
    if message.text.lower() == 'нет':
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)
    data = await state.get_data()

    await message.answer('Куда доставить посылку?', reply_markup=ReplyKeyboardRemove())


@router.message(DeliverParcelState.to_city)
async def to_city(message: Message, state: FSMContext):
    service_response = await context.places_api.search_text(message.text)
    place = None
    if 'places' in service_response:
        place = service_response['places'][0]
    if place:
        await state.set_state(DeliverParcelState.to_city_confirmation)
        await message.answer(f'Доставить сюда?: {place["formattedAddress"]}?', reply_markup=kb.city_conf_reply_mu)
        await state.update_data(to_city=place["formattedAddress"])
    else:
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
        await message.answer('Город не найден. Попробуйте еще раз')


@router.message(DeliverParcelState.to_city_confirmation, F.text.lower() == 'да')
async def date_choose(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.date_choose)
    await message.answer('Укажите желаемые даты доставки в формате: 10.02.2025 - 02.03.2025', reply_markup=ReplyKeyboardRemove())


@router.message(DeliverParcelState.date_choose)
async def date_confirmation(message: Message, state: FSMContext):
    try:
        start, end = message.text.split('-')
    except ValueError:
        await message.answer('Неверный формат даты. Попробуйте еще раз в таком формате: 10.02.2025 - 02.03.2025', reply_markup=kb.city_conf_reply_mu)
        return
    start = start.strip()
    end = end.strip()  

    if is_valid_date_range(message.text):
        await state.update_data(start_date=start, end_date=end)
        await state.set_state(DeliverParcelState.date_confirmation)
        await message.answer(f'Доставка в период с {start} по {end}?', reply_markup=kb.city_conf_reply_mu)
    else:
        await message.answer('Неверный формат даты. Попробуйте еще раз в таком формате: 10.02.2025 - 02.03.2025')


@router.message(DeliverParcelState.date_confirmation, F.text.lower() == 'да')
async def size_choose(message: Message, state: FSMContext):
    await message.answer('Есть ли ограничения по весу, объему? (Если да, то напишите)', reply_markup=kb.no_desc_kb)
    await state.set_state(DeliverParcelState.size_choose)


@router.message(DeliverParcelState.size_choose, F.text.lower() == 'пропустить')
async def skip_size_choose(message: Message, state: FSMContext):
    await state.update_data(size_choose='Не указаны')
    await show_request_details(message, state) 


@router.message(DeliverParcelState.size_choose)
async def process_size_choose(message: Message, state: FSMContext):
    await state.update_data(size_choose=message.text)
    await show_request_details(message, state) 


async def show_request_details(message: Message, state: FSMContext):
    data = await state.get_data()
    city = data.get('to_city', 'Не указано')
    start_date = data.get('start_date', 'Не указана') 
    end_date = data.get('end_date', 'Не указана')    
    size_choose = data.get('size_choose', 'Не указаны')  

    details_message = (
        f"Детали вашей заявки:\n"
        f"Город: {city}\n"
        f"Дата доставки: с {start_date} по {end_date}\n"
        f"Ограничения по весу и объему: {size_choose}\n"
    )

    await message.answer(f'Ваша заявка на доставку создана!\n{details_message}', reply_markup=kb.main_menu_reply_mu)
    await state.set_state(AppState.menu)