from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

import src.services.matcher as matcher
from src.common.states import AppState, SendParcelState
from src.common import keyboard as kb
from src.database.models import crud
from src.database.connection import db
from src.utils import get_place

from .menu import menu


router = Router()


def is_valid_date_range(date_range: str) -> bool:
    try:
        start, end = date_range.split('-')
        start = datetime.strptime(start.strip(), "%d.%m.%Y")
        end = datetime.strptime(end.strip(), "%d.%m.%Y")
        return start <= end  # Дата начала не должна быть позже даты конца
    except Exception:
        return False


@router.message(AppState.menu, or_f(F.text.lower() == 'отправить посылку', Command('/send_parcel')))
async def send_parcel(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.from_city)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)
    await message.answer('Давайте создадим заявку, мы вам сообщим когда найдется подходящий доставщик', reply_markup=kb.request_location_and_back_reply_mu)
    await message.answer('С какого города вы хотите отправить посылку?', reply_markup=kb.create_from_curr_city_mu(curr_city))

@router.message(SendParcelState.from_city, F.text.lower() == 'назад')
async def back_to_menu(message: Message, state: FSMContext):
    await menu(message, state)

@router.callback_query(SendParcelState.from_city, F.data == 'from_city:current')
async def from_city_kb(callback: CallbackQuery, state: FSMContext):
    curr_city = crud.get_city_by_tg_id(db, callback.from_user.id)
    await callback.answer()
    await state.update_data(from_city=curr_city)
    await state.set_state(SendParcelState.to_city)
    await callback.message.answer('В какой город вы хотите отправить посылку?', reply_markup=kb.request_location_and_back_reply_mu)

@router.message(SendParcelState.from_city)
async def from_city(message: Message, state: FSMContext):
    place = await get_place(message.text, message)
    if place:
        await state.update_data(from_city=place["display_name"])
        await state.set_state(SendParcelState.from_city_confirmation)
        await message.answer(f'Отправляете отсюда?: {place["display_name"]}?', reply_markup=kb.city_conf_reply_mu)
    else:
        await message.answer('Город не найден. Попробуйте еще раз')

@router.message(SendParcelState.from_city_confirmation, F.text.lower() == 'нет')
async def from_city_retry(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.from_city)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)
    await message.answer('Давайте попробуем еще раз.', reply_markup=kb.request_location_and_back_reply_mu)
    await message.answer('С какого города вы хотите отправить посылку?', reply_markup=kb.create_from_curr_city_mu(curr_city))

@router.message(SendParcelState.from_city_confirmation, F.text.lower() == 'да')
async def to_city_request(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.to_city)
    await message.answer('В какой город вы хотите отправить посылку?', reply_markup=kb.request_location_and_back_reply_mu)

@router.message(SendParcelState.to_city)
async def to_city_confirmation(message: Message, state: FSMContext):
    place = await get_place(message.text, message)
    if place:
        await state.update_data(to_city=place["display_name"])
        await state.set_state(SendParcelState.to_city_confirmation)
        await message.answer(f'Отправляете сюда?: {place["display_name"]}?', reply_markup=kb.city_conf_reply_mu)
    else:
        await message.answer('Город не найден. Попробуйте еще раз')

@router.message(SendParcelState.to_city_confirmation, F.text.lower() == 'нет')
async def to_city_retry(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.to_city)
    await message.answer('В какой город вы хотите отправить посылку?', reply_markup=kb.request_location_and_back_reply_mu)

@router.message(SendParcelState.to_city_confirmation, F.text.lower() == 'да')
async def date_choose(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.date_choose)
    await message.answer('Напишите в какие числа вам желательно отправить посылку.\nВ таком формате: 10.02.2025 - 02.03.2025', reply_markup=ReplyKeyboardRemove())

@router.message(SendParcelState.date_choose)
async def date_confirmation(message: Message, state: FSMContext):
    try:
        start, end = message.text.split('-')
    except ValueError:
        await message.answer('Неверный формат даты. Попробуйте еще раз в таком формате: 10.02.2025 - 02.03.2025')
    start = start.strip()
    end = end.strip()  

    if is_valid_date_range(message.text):
        await state.update_data(start_date=start, end_date=end)
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
    await callback.answer()
    await state.update_data(size_choose=callback.data.replace('size:', ''))
    await callback.message.answer('Напишите дополнительные требования или примечания к доставке', reply_markup=kb.no_desc_kb)
    await state.set_state(SendParcelState.description)

@router.callback_query(SendParcelState.description, F.text.lower() == 'пропустить')
async def no_desc(message: Message, state: FSMContext):
    await state.update_data(description='Не указаны')
    await show_request_details(message, state)

@router.message(SendParcelState.description)
async def desc_text(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await show_request_details(message, state)


async def show_request_details(message: Message, state: FSMContext):
    SIZE_TRANSLATION = {
        "small": "Маленькая",
        "medium": "Средняя",
        "large": "Большая",
        "extra_large": "Крупногабаритная"
    }

    data = await state.get_data()
    from_city = data.get('from_city', 'Не указано')
    to_city = data.get('to_city', 'Не указано')
    start_date = data.get('start_date', 'Не указана')
    end_date = data.get('end_date', 'Не указана')
    size_choose = data.get('size_choose', 'Не указаны')
    size_choose = SIZE_TRANSLATION.get(size_choose, size_choose)
    description = data.get('description', 'Не указаны')

    details_message = (
        f"Детали вашей заявки:\n"
        f"Город отправления: {from_city}\n"
        f"Город назначения: {to_city}\n"
        f"Дата отправления: с {start_date} по {end_date}\n"
        f"Вес и габариты: {size_choose}\n"
        f"Дополнительные требования: {description}\n"
    )

    
    send_req = crud.create_send_request(db, message.from_user.id, from_city, to_city, start_date, end_date, size_choose, description)
    print(send_req)


    await message.answer(f'Статус вашей заявки: Открыта.\nНомер заявки: {send_req.id}. В ближайшее время мы свяжем вас с курьером.\n{details_message}', reply_markup=kb.main_menu_open_req_reply_mu)
    await state.set_state(AppState.menu)

    await matcher.match_send_request(send_req)
