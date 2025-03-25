from datetime import datetime


from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery


import src.services.matcher as matcher
from src.services import sheets
from src.services import request_reminder
from src.common.states import AppState, DeliverParcelState
from src.common import keyboard as kb
from src.database.models import crud
from src.database import db
from src.utils import get_place
from src.aiogram_calendar import DialogCalendar, DialogCalendarCallback
from src.handlers import menu


router = Router()


@router.message(AppState.menu, or_f(F.text.lower() == 'хочу доставить посылку', Command('/deliver_parcel')))
async def from_city_choose(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.from_city)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)

    await message.answer('Буду рад помочь с этим! Для этого я задам Вам уточняющие вопросы.', reply_markup=kb.request_location_and_back_reply_mu)
    await message.answer('<b>Откуда</b> Вы хотите взять заказ (посылку)? (Страна, город)', reply_markup=kb.create_from_curr_city_mu(curr_city), parse_mode='HTML')
    
@router.message(DeliverParcelState.from_city, F.text.lower() == 'назад')
async def back_to_menu(message: Message, state: FSMContext):
    await menu.handle_menu(message, state)


@router.callback_query(DeliverParcelState.from_city, F.data == 'from_city:current')
async def from_city_kb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
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
        await message.answer(f'Вы хотите взять заказ (посылку) из города: {place["display_name"]}?', reply_markup=kb.city_conf_reply_mu)
    else:
        await message.answer('Город не найден. Попробуйте еще раз')


@router.message(DeliverParcelState.from_city_confirmation, F.text.lower() == 'неверный адрес')
async def from_city_retry(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.from_city)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)
    await message.answer('Прошу прощения, наверное я не правильно Вас понял!', reply_markup=kb.request_location_and_back_reply_mu)
    await message.answer('Пожалуйста, отправьте название Вашего города еще раз.\nУбедитесь, что Вы не допустили ошибок.', reply_markup=kb.create_from_curr_city_mu(curr_city))

    
@router.message(DeliverParcelState.to_city_confirmation, F.text.lower() == 'нет')
@router.message(DeliverParcelState.from_city_confirmation, F.text.lower() == 'да')
async def deliver_parcel(message: Message, state: FSMContext, user = None):
    if user is None:
        user = message.from_user
    await state.set_state(DeliverParcelState.to_city)
    await message.answer('<b>Куда</b> Вы готовы доставить заказ (посылку)?\n(Страна, город)', reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Любой пункт назначения')], [KeyboardButton(text='Назад')]], resize_keyboard=True), parse_mode='HTML')

@router.message(DeliverParcelState.to_city, F.text.lower() == 'любой пункт назначения')
async def to_any_city(message: Message, state: FSMContext):
    await message.answer('Выбирая опцию "Любой пункт назначения", Вы подтверждаете, что из города, где вы находитесь (Указали в предыдущем вопросе), Вы готовы взять заказ (Посылку) и доставить его в любой пункт назначения (Любой город, страну)', reply_markup=ReplyKeyboardRemove())
    await state.update_data(to_city='*')
    await date_choose(message, state)

@router.message(DeliverParcelState.to_city, F.text.lower() == 'назад')
async def back_to_from_city(message: Message, state: FSMContext):
    await from_city_choose(message, state)

@router.message(DeliverParcelState.to_city)
async def to_city(message: Message, state: FSMContext):
    
    place = await get_place(message.text, message)

    if place:
        await state.set_state(DeliverParcelState.to_city_confirmation)
        await message.answer(f'Вы хотите доставить посылку в этот город: {place["display_name"]}?', reply_markup=kb.city_conf_reply_mu)
        await state.update_data(to_city=place["display_name"])
    else:
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
        await message.answer('Город не найден. Попробуйте еще раз')

@router.message(DeliverParcelState.to_city_confirmation, F.text.lower() == 'да')
async def date_choose(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.date_choose)
    await state.update_data(start_date=None, end_date=None)
    await message.answer(message.chat.id, text='Выберите пожалуйста', reply_markup=ReplyKeyboardRemove())
    await message.answer('Укажите, в какие числа Вам желательно взять заказ (посылку) у клиента (отправителя).\n<i>Чем шире охват дат, которые Вы укажете, тем больше шанс найти подходящего отправителя</i>', parse_mode='HTML', reply_markup=await DialogCalendar().start_calendar())
    

@router.callback_query(DeliverParcelState.date_choose, DialogCalendarCallback.filter())
async def process_calendar(callback_query: CallbackQuery, callback_data: DialogCalendarCallback, state: FSMContext):
    try:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        max_date = datetime(today.year + 1, today.month, today.day)
        calendar = DialogCalendar()
        calendar.set_dates_range(min_date=today, max_date=max_date)
        selected, date = await calendar.process_selection(callback_query, callback_data)
        if not selected:
            return
        
        state_data = await state.get_data()
        if "start_date" not in state_data or not isinstance(state_data["start_date"], datetime):
            await state.update_data(start_date=date)
            end_calendar = DialogCalendar()
            end_calendar.set_dates_range(min_date=date, max_date=max_date)
            await callback_query.message.answer(
                f'Вы выбрали {date.strftime("%d.%m.%Y")} как <b>начальную</b> дату. '
                f'Теперь выберите <b>крайний</b> день, когда встреча с отправительем еще возможна.', parse_mode='HTML',
                reply_markup=await end_calendar.start_calendar()
            )
        else:
            start_date = state_data["start_date"]
            # Validate that end date is after start date
            if date < start_date:
                await callback_query.message.answer(
                    "Конечная дата должна быть после начальной даты. Пожалуйста, выберите другую дату.",
                    reply_markup=await DialogCalendar().start_calendar()
                )
                return
                
            await state.update_data(end_date=date)
            await state.set_state(DeliverParcelState.date_confirmation)
            await callback_query.message.answer(
                f"Вы хотите взять посылку у отправителя с {start_date.strftime('%d.%m.%Y')} по {date.strftime('%d.%m.%Y')}.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text='Да'), KeyboardButton(text='Я хочу изменить даты')]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
            )
    except Exception as e:
        print(f"Calendar error: {e}")
        await callback_query.message.answer(
            "Произошла ошибка при обработке выбора даты. Пожалуйста, попробуйте снова.",
            reply_markup=await DialogCalendar().start_calendar()
        )
        
@router.message(DeliverParcelState.date_choose)
async def date_choose_retry(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, выберайте по календарю')
    
@router.message(DeliverParcelState.date_confirmation, F.text.lower() == 'я хочу изменить даты')
async def date_retry(message: Message, state: FSMContext):
    await date_choose(message, state)

@router.message(DeliverParcelState.date_confirmation, F.text.lower() == 'да')
async def size_choose(message: Message, state: FSMContext):
    await message.answer('Выберите пожалуйтса', reply_markup=ReplyKeyboardRemove())
    await message.answer('Какую посылку Вы хотите взять?', reply_markup=kb.sizes_kb_del)
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
    start_date = data.get('start_date', None)
    end_date = data.get('end_date', None)
    size_choose = data.get('size_choose', 'Не указаны')

    delivery_req = crud.create_delivery_request(db, user.id, from_city, to_city, start_date, end_date, size_choose)

    details_message = (
        f"Детали заявки:\n"
        f"Статус заявки: Открыта.\n"
        f"Номер заявки: {delivery_req.id}.\n"
        f"Город отправления: {from_city}\n"
        f"Город назначения: {to_city}\n"
        f"Дата отправления: с {start_date} по {end_date}\n"
        f"Вес и габариты: {size_choose}\n"
    )
    # TODO: FIX sheets, request_reminder
    sheets.record_add_deliver_req(delivery_req)
    await request_reminder.send_request(delivery_req)
    await message.answer(f'🎉Поздравляю! Я открыл для Вас заявку на поиск заказа. Я сообщу, как только по Вашей заявке найдется посылка!🙌🏻\n{details_message}', reply_markup=kb.main_menu_open_req_reply_mu)
    await state.set_state(AppState.menu)

    await matcher.match_delivery_request(delivery_req)