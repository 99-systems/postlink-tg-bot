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




@router.message(SendParcelState.city_confirmation, F.text.lower() == 'нет')
@router.message(AppState.menu, or_f(F.text.lower() == 'Отправить посылку', Command('/send_parcel')))
async def send_parcel(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.from_city)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)
    data = await state.get_data()

    if('try_count' in data):
        await message.answer('Откуда вы отправляетесь?\nЕсли не можете найти, можно указать страну с городом.\nКазахстан, Алматы')
    await message.answer('Откуда вы отправляетесь?', reply_markup=kb.create_curr_city_mu(curr_city))

@router.callback_query(SendParcelState.from_city, F.data == 'city:current')
async def from_city_kb(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SendParcelState.to_city)
    curr_city = crud.get_city_by_tg_id(db, callback.from_user.id)
    await callback.answer('')
    await to_city(callback.message, state)


@router.message(SendParcelState.from_city)
async def from_city(message: Message, state: FSMContext):
    
    service_response = await context.places_api.search_text(message.text)
    
    place = None
    
    if 'places' in service_response:
        place = service_response['places'][0]
    
    if place:
        await state.set_state(SendParcelState.from_city_confirmation)
        await message.answer(f'Отправляетесь отсюда?: {place["formattedAddress"]}?', reply_markup=kb.city_conf_reply_mu)    
        await state.update_data(city=place["formattedAddress"])
    else:
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)

        await message.answer('Город не найден. Попробуйте еще раз')

@router.message(SendParcelState.from_city_confirmation, F.text.lower() == 'да')
async def to_city(message: Message, state: FSMContext):
    await state.set_state(SendParcelState.to_city)
    curr_city = crud.get_city_by_tg_id(db, message.from_user.id)
    await message.answer('Куда вы отправляетесь?', reply_markup=kb.create_curr_city_mu(curr_city))
