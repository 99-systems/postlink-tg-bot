from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import Command, or_f
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery

import src.services.matcher as matcher
from src.common.states import AppState, DeliverParcelState
from src.common import keyboard as kb
from src.database.models import crud
from src.database.connection import db
from src.utils import get_place
from src.aiogram_calendar import DialogCalendar, DialogCalendarCallback, get_user_locale

from .menu import menu


router = Router()

@router.message(F.text.casefold() == 'abc')
async def test(message: Message):
    await message.answer('abc')

@router.message(AppState.menu, or_f(F.text.lower() == 'доставить посылку', Command('/deliver_parcel')))
async def from_city_choose(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.from_city)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)

    await message.answer('Давайте создадим заявку, и если появится подходящая посылка, мы вам сообщим!', reply_markup=kb.request_location_and_back_reply_mu)
    await message.answer('Откуда начинается ваш маршрут?', reply_markup=kb.create_from_curr_city_mu(curr_city))
    
@router.message(DeliverParcelState.from_city, F.text.lower() == 'назад')
async def back_to_menu(message: Message, state: FSMContext):
    await menu(message, state)


@router.callback_query(DeliverParcelState.from_city, F.data == 'from_city:current')
async def from_city_kb(callback: CallbackQuery, state: FSMContext):
    curr_city = crud.get_city_by_tg_id(db, callback.from_user.id)
    place = {}
    place['display_name'] = curr_city
    await from_city_confirmation(callback.message, state, place)


@router.message(DeliverParcelState.from_city)
async def from_city(message: Message, state: FSMContext):
    if message:
        place = await get_place(message.text, message)
        await from_city_confirmation(message, state, place)

async def from_city_confirmation(message: Message, state: FSMContext, place):
    if place:
        await state.update_data(from_city=place["display_name"])
        await state.set_state(DeliverParcelState.from_city_confirmation)
        await message.answer(f'Отправляете посылку отсюда?: {place["display_name"]}?', reply_markup=kb.city_conf_reply_mu)
    else:
        await message.answer('Город не найден. Попробуйте еще раз')


@router.message(DeliverParcelState.from_city_confirmation, F.text.lower() == 'нет')
async def from_city_retry(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.from_city)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)
    await message.answer('Давайте попробуем еще раз.', reply_markup=kb.request_location_and_back_reply_mu)
    await message.answer('Откуда начинается ваш маршрут?', reply_markup=kb.create_from_curr_city_mu(curr_city))

    
@router.message(DeliverParcelState.to_city_confirmation, F.text.lower() == 'нет')
@router.message(DeliverParcelState.from_city_confirmation, F.text.lower() == 'да')
async def deliver_parcel(message: Message, state: FSMContext, user = None):
    if user is None:
        user = message.from_user
    await state.set_state(DeliverParcelState.to_city)
    await message.answer('Куда вы отправляетесь?', reply_markup=kb.request_location_and_back_reply_mu)

@router.message(DeliverParcelState.to_city, F.text.lower() == 'назад')
async def back_to_from_city(message: Message, state: FSMContext):
    await from_city_choose(message, state)

@router.message(DeliverParcelState.to_city)
async def to_city(message: Message, state: FSMContext):
    
    place = await get_place(message.text, message)

    if place:
        await state.set_state(DeliverParcelState.to_city_confirmation)
        await message.answer(f'Отправляетесь сюда?: {place["display_name"]}?', reply_markup=kb.city_conf_reply_mu)
        await state.update_data(to_city=place["display_name"])
    else:
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
        await message.answer('Город не найден. Попробуйте еще раз')

@router.message(DeliverParcelState.to_city_confirmation, F.text.lower() == 'да')
async def date_choose(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.date_choose)
    await message.answer('Какого числа Вы отправляетесь в пункт назначения?', reply_markup=ReplyKeyboardRemove())
    await message.answer('Выбирите пожалуйста ниже', reply_markup=await DialogCalendar(locale=await get_user_locale(message.from_user)).start_calendar())
    

@router.callback_query(DialogCalendarCallback.filter())
async def date_confirmation(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)
    if selected:
        deliver_date = date.strftime("%d.%m.%Y")
        await state.update_data(deliver_date=deliver_date)
        await state.set_state(DeliverParcelState.date_confirmation)

        await callback_query.message.answer(
            f'Вы отправляетесь в {deliver_date} числа?', reply_markup=kb.city_conf_reply_mu
        )
        
@router.message(DeliverParcelState.date_choose)
async def date_choose_retry(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, выберайте по календарю')

@router.message(DeliverParcelState.date_confirmation, F.text.lower() == 'да')
async def size_choose(message: Message, state: FSMContext):
    await message.answer('Выберите пожалуйтса', reply_markup=ReplyKeyboardRemove())
    await message.answer('Какие ограничения по весу или обьему посылки?', reply_markup=kb.sizes_kb_del)
    await state.set_state(DeliverParcelState.size_choose)


@router.callback_query(DeliverParcelState.size_choose, F.data.startswith('size:'))
async def process_size_choose(callback: CallbackQuery, state: FSMContext):
    SIZE_TRANSLATION = {
        "small": "Маленькая",
        "medium": "Средняя",
        "large": "Большая",
        "extra_large": "Крупногабаритная",
        "skip": "Не указаны"
    }

    size_key = callback.data.split(':')[1]
    size_choose = SIZE_TRANSLATION.get(size_key, "Не указаны")

    await state.update_data(size_choose=size_choose)
    await callback.answer()
    await show_request_details(callback.message, state, user = callback.from_user)

async def show_request_details(message: Message, state: FSMContext, user = None):
    if user is None:
        user = message.from_user

    data = await state.get_data()
    from_city = data.get('from_city', 'Не указано')
    to_city = data.get('to_city', 'Не указано')
    deliver_date = data.get('deliver_date', 'Не указана')
    size_choose = data.get('size_choose', 'Не указаны')


    details_message = (
        f"Детали вашей заявки:\n"
        f"Город отправления: {from_city}\n"
        f"Город назначения: {to_city}\n"
        f"Дата отправления: {deliver_date}\n"
        f"Вес и габариты: {size_choose}\n"
    )
    
    delivery_req = crud.create_delivery_request(db, user.id, from_city, to_city, deliver_date, size_choose)
    print(vars(delivery_req))

    await message.answer(f'Статус вашей заявки: Открыта.\nНомер заявки: {delivery_req.id}. В ближайшее время мы свяжем вас с отправителем.\n{details_message}', reply_markup=kb.main_menu_open_req_reply_mu)
    await state.set_state(AppState.menu)

    await matcher.match_delivery_request(delivery_req)