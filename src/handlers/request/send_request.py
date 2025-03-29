from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

import src.services.matcher as matcher
from src.services import request_reminder, sheets
from src.common.states import AppState, SendParcelState
from src.common import keyboard as kb
from src.database.models import crud
from src.database import db
from src.utils import get_place
from src.aiogram_calendar import DialogCalendar, DialogCalendarCallback
from src.handlers import menu

router = Router()


@router.message(AppState.menu, or_f(F.text.lower() == 'хочу отправить посылку', Command('/send_parcel')))
async def send_parcel(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.from_city)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)
    await message.answer('Буду рад помочь с этим! Для этого я задам Вам уточняющие вопросы.', reply_markup=kb.request_location_and_back_reply_mu)
    await message.answer('<b>Откуда</b> Вы хотите отправить посылку? (Страна, город)', reply_markup=kb.create_from_curr_city_mu(curr_city), parse_mode='HTML')


@router.message(SendParcelState.from_city, F.text.lower() == 'назад')
async def back_to_menu(message: Message, state: FSMContext):
    await menu.handle_menu(message, state)


@router.callback_query(SendParcelState.from_city, F.data == 'from_city:current')
async def from_city_kb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    curr_city = crud.get_city_by_tg_id(db, callback.from_user.id)
    place = await get_place(curr_city, callback.message)

    if place:
        await state.update_data(from_city=place["display_name"])
        await state.set_state(SendParcelState.from_city_confirmation)
        await callback.message.answer(f'Вы хотите отправить посылку из города: {place["display_name"]}?', reply_markup=kb.city_conf_reply_mu)
    else:
        await callback.message.answer('Город не найден. Попробуйте еще раз')


@router.message(SendParcelState.from_city)
async def from_city(message: Message, state: FSMContext):
    place = await get_place(message.text, message)
    if place:
        await state.update_data(from_city=place["display_name"])
        await state.set_state(SendParcelState.from_city_confirmation)
        await message.answer(f'Вы хотите отправить посылку из города: {place["display_name"]}?', reply_markup=kb.city_conf_reply_mu)
    else:
        await message.answer('Город не найден. Попробуйте еще раз')


@router.message(SendParcelState.from_city_confirmation, F.text.lower() == 'неверный адрес')
async def from_city_retry(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.from_city)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)
    await message.answer('Прошу прощения, наверное, я не правильно Вас понял!', reply_markup=kb.request_location_and_back_reply_mu)
    await message.answer('Пожалуйста, отправьте название Вашего города еще раз. Убедитесь, что Вы не допустили ошибок.', reply_markup=kb.create_from_curr_city_mu(curr_city))


@router.message(SendParcelState.from_city_confirmation, F.text.lower() == 'да')
async def to_city_request(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.to_city)
    await message.answer('<b>Куда</b> Вы хотите отправить посылку? (Страна, город)', reply_markup=kb.request_location_and_back_reply_mu, parse_mode='HTML')


@router.message(SendParcelState.to_city, F.text.lower() == 'назад')
async def back_to_from_city(message: Message, state: FSMContext):
    # Get the current from_city to display it again
    state_data = await state.get_data()
    from_city = state_data.get('from_city', '')
    
    await state.set_state(SendParcelState.from_city_confirmation)
    await message.answer(f'Вы хотите отправить посылку из города: {from_city}?', reply_markup=kb.city_conf_reply_mu)


@router.message(SendParcelState.to_city)
async def to_city_confirmation(message: Message, state: FSMContext):
    place = await get_place(message.text, message)
    if place:
        await state.update_data(to_city=place["display_name"])
        await state.set_state(SendParcelState.to_city_confirmation)
        await message.answer(f'Вы хотите отправить посылку в этот город: {place["display_name"]}?', reply_markup=kb.city_conf_reply_mu)
    else:
        await message.answer('Город не найден. Попробуйте еще раз')


@router.message(SendParcelState.to_city_confirmation, F.text.lower() == 'неверный адрес')
async def to_city_retry(message: Message, state: FSMContext):
    await message.answer('Прошу прощения, наверное, я не правильно Вас понял! Пожалуйста, отправьте название города еще раз. Убедитесь, что Вы не допустили ошибок.', reply_markup=ReplyKeyboardRemove())
    await state.set_state(SendParcelState.to_city)

@router.message(SendParcelState.to_city_confirmation, F.text.lower() == 'да')
async def date_choose(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.date_choose)
    await state.update_data(start_date=None, end_date=None)
    
    await message.answer('Выберите пожалуйста', reply_markup=ReplyKeyboardRemove())
    await message.answer('Укажите, в какие числа Вам удобно передать посылку курьеру.\n<i>Чем шире охват дат, которые Вы укажете, тем больше шанс найти подходящего курьера</i>', parse_mode='HTML', reply_markup=await DialogCalendar().start_calendar())
    

@router.callback_query(SendParcelState.date_choose, DialogCalendarCallback.filter())
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
                f'Теперь выберите <b>крайний</b> день, когда встреча с курьером еще возможна.', parse_mode='HTML',
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
            await state.set_state(SendParcelState.date_confirmation)
            await callback_query.message.answer(
                f"В период с {start_date.strftime('%d.%m.%Y')} по {date.strftime('%d.%m.%Y')} Вам удобно передать посылку курьеру.",
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


@router.message(SendParcelState.date_confirmation, F.text.lower() == 'да')
async def size_choose(message: Message, state: FSMContext):
    await message.answer('Выберите пожалуйтса', reply_markup=ReplyKeyboardRemove())
    await message.answer('Какой вес и габариты посылки?', reply_markup=kb.sizes_kb)
    await state.set_state(SendParcelState.size_confirmation)
    

@router.message(SendParcelState.date_confirmation, F.text.lower() == 'я хочу изменить даты')
async def date_retry(message: Message, state: FSMContext):
    await date_choose(message, state)


@router.callback_query(SendParcelState.size_confirmation, F.data.startswith('size:'))
async def size_kb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    size = callback.data.replace('size:', '')
    await state.update_data(size_choose=size)
    await callback.message.answer('Есть ли дополнительные требования или примечания для курьера? (Хрупкие товары, электроника, продукты питания)', reply_markup=kb.no_desc_kb)
    await state.set_state(SendParcelState.description)


@router.callback_query(SendParcelState.description, F.data == 'no_desc')
async def no_desc(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(description='Не указаны')
    await show_request_details(callback.message, state)


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

    try:
        data = await state.get_data()
        from_city = data.get('from_city', 'Не указано')
        to_city = data.get('to_city', 'Не указано')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        size_choose = data.get('size_choose', 'Не указаны')
        size_choose = SIZE_TRANSLATION.get(size_choose, size_choose)
        description = data.get('description', 'Не указаны')

        send_req = crud.create_send_request(db, message.from_user.id, from_city, to_city, start_date.strftime("%d.%m.%Y"), end_date.strftime("%d.%m.%Y"), size_choose, description)
        details_message = (
            f"Детали заявки:\n"
            "Статус вашей заявки: Открыта.\n"
            f"Номер заявки: {send_req.id}.\n"
            f"Город отправления: {from_city}\n"
            f"Город назначения: {to_city}\n"
            f"Дата отправления: с {start_date} по {end_date}\n"
            f"Вес и габариты: {size_choose}\n"
            f"Дополнительные требования: {description}\n"
        )
        sheets.record_add_send_req(send_req)
        await request_reminder.send_request(send_req)
        await message.answer(
            f'🎉Поздравляю! Я открыл для Вас заявку на поиск курьера. Я сообщу, как только по Вашей заявке найдется доставщик!🙌🏻\n\n{details_message}', 
            reply_markup=kb.main_menu_open_req_reply_mu
        )
        await state.set_state(AppState.menu)

        await matcher.match_send_request(send_req)
    except Exception as e:
        print(f"Error creating request: {e}")
        await message.answer(
            "Произошла ошибка при создании заявки. Пожалуйста, попробуйте снова.",
            reply_markup=kb.main_menu_reply_mu
        )
        await state.set_state(AppState.menu)