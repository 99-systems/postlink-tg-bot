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
    await message.answer('Прошу прощения, наверное, я неправильно Вас понял!', reply_markup=kb.request_location_and_back_reply_mu)
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
        await state.update_data(try_count=(data.get('try_count', 0) + 1))
        await message.answer('Город не найден. Попробуйте еще раз')
        
@router.message(DeliverParcelState.to_city_confirmation, F.text.lower() == 'неверный адрес')
async def to_city_retry(message: Message, state: FSMContext):
    await message.answer('Прошу прощения, наверное, я неправильно Вас понял! Пожалуйста, отправьте название города еще раз. Убедитесь, что Вы не допустили ошибок.', reply_markup=ReplyKeyboardRemove())
    await state.set_state(DeliverParcelState.to_city)

@router.message(DeliverParcelState.to_city_confirmation, F.text.lower() == 'да')
async def date_choose(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.date_choose)
    await state.update_data(start_date=None, end_date=None)
    await message.answer('Укажите, в какие числа Вам желательно взять заказ (посылку) у клиента (отправителя).', reply_markup=ReplyKeyboardRemove())
    await message.answer('<i>Чем шире охват дат, которые Вы укажете, тем больше шанс найти подходящего отправителя</i>', parse_mode='HTML', reply_markup=await DialogCalendar().start_calendar())
    

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
    await message.answer('Какую посылку Вы хотите взять?', reply_markup=ReplyKeyboardRemove())
    await message.answer('Укажите категорию  посылки', reply_markup=kb.sizes_kb_del)
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
    
    await offer_description(callback.message, state)


async def offer_description(message: Message, state: FSMContext):
    await message.answer('Есть ли дополнительные требования или примечания к предмету посылки ? (Например: не беру хрупкие товары, электронику, продукты питания)', reply_markup=kb.no_desc_kb)
    await state.set_state(DeliverParcelState.description)

@router.message(DeliverParcelState.description)
async def description(message: Message, state: FSMContext):
    if message.text.lower() == 'пропустить':
        await show_request_details(message, state)
    else:
        await state.update_data(description=message.text)
        await show_request_details(message, state)

async def show_request_details(message: Message, state: FSMContext, tg_user_id = None):
    if tg_user_id is None:
        tg_user_id = message.from_user

    data = await state.get_data()
    from_city = data.get('from_city', 'Не указано')
    to_city = data.get('to_city', 'Не указано')
    start_date = data.get('start_date', None)
    end_date = data.get('end_date', None)
    size_choose = data.get('size_choose', 'Не указаны')
    description = data.get('description', 'Не указаны')

    delivery_req = crud.create_delivery_request(db, tg_user_id, from_city, to_city, start_date, end_date, size_choose, description)

    details_message = (
        f"Детали заявки:\n"
        "<b>Заявка на поиск заказа (Посылки)</b>\n"
        f"📌Номер заявки: <b>{delivery_req.id}</b>.\n"
        "🛎Статус: <b>Активна</b>.\n"
        f"🛫Город отправления: <b>{from_city}</b>\n"
        f"🛫Город назначения: <b>{to_city}</b>\n"
        f"🗓Даты: <b>{start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}</b>\n"
        f"📊Категория посылки: {size_choose}\n"
        f"📋Дополнительные примечания: <b>{description}</b>\n"
    )
    # TODO: FIX sheets, request_reminder
    sheets.record_add_deliver_req(delivery_req)
    await request_reminder.send_request(delivery_req)
    await message.answer(f'🎉Поздравляю! Я открыл для Вас заявку на поиск заказа. Я сообщу, как только по Вашей заявке найдется посылка!🙌🏻\n{details_message}', reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    await state.update_data(delivery_req_id=delivery_req.id)
    await matcher.match_delivery_request(delivery_req)

    user = crud.get_user_by_tg_id(db, tg_user_id)
    open_requests = crud.get_all_open_delivery_requests_by_user_id(db, user.id)

    if (len(open_requests) < 2):
        await handle_offer_another_delivery_request(message, state)
    else:
        await handle_no_another_delivery_request(message, state)
    
    
async def handle_offer_another_delivery_request(message: Message, state: FSMContext):
    await state.set_state(DeliverParcelState.another_delivery_request)
    await message.answer('Хотите взять еще одну посылку?', reply_markup=kb.confirmation_reply_mu)

@router.message(AppState.menu, F.text.lower() == 'создать еще одну заявку')
@router.message(DeliverParcelState.another_delivery_request, F.text.lower() == 'да')
async def handle_another_delivery_request(message: Message, state: FSMContext):
    
    state_data = await state.get_data()
    
    delivery_req_id = state_data.get('delivery_req_id', None)
    delivery_req = crud.get_delivery_request_by_id(db, delivery_req_id)
    
    await state.set_state(DeliverParcelState.another_delivery_request_confirmation)
    await message.answer(f'Отлично! Создаем еще одну заявку на поиск заказа (посылки). Вы хотите найти заказ по такому же маршруту?\n{delivery_req.from_date} - {delivery_req.to_date}\n{delivery_req.from_location} - {delivery_req.to_location}', reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Да')], [KeyboardButton(text='Хочу указать другой маршрут')], [KeyboardButton(text='Отмена')]], resize_keyboard=True))

@router.message(DeliverParcelState.another_delivery_request, F.text.lower() == 'нет')
async def handle_no_another_delivery_request(message: Message, state: FSMContext):
    await menu.handle_menu(message, state)
    

@router.message(DeliverParcelState.another_delivery_request)
async def handle_no_match_another_delivery_request(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, выберите один из вариантов', reply_markup=kb.confirmation_reply_mu)
    

@router.message(DeliverParcelState.another_delivery_request_confirmation, F.text.lower() == 'отмена')
async def handle_cancel_another_delivery_request(message: Message, state: FSMContext):
    await handle_no_another_delivery_request(message, state)
    
@router.message(DeliverParcelState.another_delivery_request_confirmation, F.text.lower() == 'хочу указать другой маршрут')
async def handle_change_route_another_delivery_request(message: Message, state: FSMContext):
    await message.answer('К сожалению, несколько одновременных заявок можно открыть только по одинаковым маршрутам. Если Вы хотите открыть заявку по новому маршруту, то необходимо завершить текущую заявку и после открыть новую.', reply_markup=ReplyKeyboardRemove())
    await handle_no_another_delivery_request(message, state)
    
@router.message(DeliverParcelState.another_delivery_request_confirmation, F.text.lower() == 'да')
async def handle_another_delivery_request_confirmation(message: Message, state: FSMContext):
    await size_choose(message, state)