from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, or_f
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram import F


import src.common.keyboard as kb
import src.context as context
from src.common.states import AppState, RegistrationState
from src.database.models import crud
from src.database import db

from src.utils import get_place

from src.handlers.auth import router, OTP_CODE_LENGTH
from src.handlers.auth.common import handle_success_auth, handle_back_start
from .filters import PhoneNumberFilter
from .utils import format_phone_number

from src.services import sheets 


@router.message(RegistrationState.city, F.text.lower() == 'назад')
@router.message(AppState.auth, or_f(F.text.lower() == 'регистрация', Command('register')))   
async def handle_registration(message: Message, state: FSMContext):
    
    
    tg_user = crud.get_tg_user(db, message.from_user.id)  
    
    
    if tg_user.accepted_terms:
        await state.set_state(RegistrationState.name)
        await message.reply('Как Вас зовут?', reply_markup=kb.back_reply_mu)
    else:
        await message.answer('''
<b>Важно знать!</b>

❗ PostLink не участвует в доставке и не проверяет содержимое посылок.
Мы только находим и связываем нужные контакты за небольшую плату.
Вся ответственность за передачу и безопасность сделки лежит на самих пользователях.

‼️Перед началом работы ознакомьтесь с Пользовательским соглашением:
''', parse_mode='HTML')    
        await state.set_state(AppState.terms)
        await send_terms(message, state)
    

@router.message(F.text.lower() == 'согласен', AppState.terms)
async def accept_terms(message: Message, state: FSMContext):
    crud.accept_terms(db, message.from_user.id)
    
    await state.set_state(RegistrationState.name)
    await message.reply('Как Вас зовут?', reply_markup=kb.back_reply_mu)
    
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
   


@router.message(RegistrationState.name)
@router.message(RegistrationState.city_confirmation, F.text.lower() == 'неверный адрес')
async def handle_name(message: Message, state: FSMContext):

    current_state = await state.get_state()
    
    if current_state == RegistrationState.name:
        await state.update_data(name=message.text)
    
    if message.text.lower() == 'нет':
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
    
    await state.set_state(RegistrationState.city)

    state_data = await state.get_data()
    name = state_data.get('name', message.text)

    text = f'{name}, В каком городе Вы находитесь?\n\n<i>Можно указать название города или отправить свою геолокацию.</i>'

    if 'try_count' in state_data and state_data['try_count'] > 0:
        text = f'{name}, В каком городе Вы находитесь?\n\n<i>Если не можете найти, можно указать страну с городом.\nКазахстан, Алматы</i>'
    await message.answer(text, reply_markup=kb.request_location_and_back_reply_mu, parse_mode='HTML')
    
@router.message(RegistrationState.city)
async def handle_city(message: Message, state: FSMContext):
    
    place = await get_place(message.text, message)
    
    if place:
        await state.set_state(RegistrationState.city_confirmation)
        await message.answer(f'Вы находитесь в городе: {place["display_name"]}?', reply_markup=kb.city_conf_reply_mu)    
        await state.update_data(city=place["display_name"])
    else:
        data = await state.get_data()
        await state.update_data(try_count=data.get('try_count', 0) + 1)
        await message.answer('Город не найден. Попробуйте еще раз', reply_markup=kb.request_location_and_back_reply_mu)

    
@router.message(RegistrationState.city_confirmation, F.text.lower() == 'да')
async def handle_city_confirmation(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.phone)
    await message.answer('Можно узнать Ваш сотовый номер телефона, привязанный к Whatsapp?', reply_markup=kb.phone_reply_mu)
    
    
    
@router.message(RegistrationState.phone, PhoneNumberFilter())
async def handle_phone_number(message: Message, state: FSMContext):
    
    user_phone = format_phone_number(message.contact.phone_number if message.contact else message.text)
    await state.update_data(phone=user_phone)
    
    user = crud.get_user_by_phone(db, user_phone)
    if user:
        await message.reply('Пользователь с таким номером телефона уже существует, попробуйте войти')
        await state.set_state({}) 
        await handle_back_start(message, state)
        return
    
    response = await context.otp_service.send_otp(user_phone, OTP_CODE_LENGTH)
    if 'message' in response:
        await message.reply(f'Я выслал Вам код подтверждения на WhatsApp по номеру {user_phone}. Прошу отправить мне полученный 4-х значный код.', reply_markup=kb.not_received_otp_code_reply_mu)
        await state.update_data(phone=user_phone)
        await state.update_data(wrong_otp_count=(await state.get_data()).get('wrong_otp_count', 0))
        await state.set_state(RegistrationState.otp_code)
    else:
        await message.reply(f'Мне не удалось отправить код на WhatsApp по вашему номеру {user_phone}.\nПожалуйста, убедитесь что номер корректный.')
        await handle_city_confirmation(message, state)
        return
    
@router.message(RegistrationState.phone, F.text.lower() == 'код все еще не был отправлен')
async def handle_final_code_not_sent(message: Message, state: FSMContext):
    await message.answer('В случае, если вы не получили код, при этом указав правильный номер Whatsapp в формате: +7705 777 7777, то предлагаем обратиться в Службу Поддержки', reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Служба поддержки')]], resize_keyboard=True))
    await state.set_state(RegistrationState.phone)
    

@router.message(RegistrationState.phone, F.text.lower() == 'служба поддержки')
async def handle_support(message: Message, state: FSMContext):
    from src.handlers.menu import handle_support
    await handle_support(message, state)

@router.message(RegistrationState.phone)
async def handle_invalid_phone_number(message: Message, state: FSMContext):
    await message.answer('Это не похоже на номер телефона, давайте попробуем снова! Прошу написать номер телефона в таком формате: +7/8XXXXXXXXXX', reply_markup=kb.phone_reply_mu)


@router.message(RegistrationState.request_otp_code, F.text.lower() == 'отправить код')
async def handle_request_otp_code(message: Message, state: FSMContext):
    data = await state.get_data()
    user_phone = data.get('phone')
    
    response = await context.otp_service.send_otp(user_phone, OTP_CODE_LENGTH)
    if 'message' in response:
        await message.reply(f'Я выслал Вам код подтверждения на WhatsApp по номеру {user_phone}. Прошу отправить мне полученный 4-х значный код.', reply_markup=kb.not_received_otp_code_reply_mu)
        await state.update_data(phone=user_phone)
        await state.set_state(RegistrationState.otp_code)
    else:
        await message.reply('Попробуйте еще раз')
        await state.set_state(RegistrationState.phone)
        return

@router.message(RegistrationState.otp_code, F.text.lower() == 'код не был отправлен')
async def handle_code_not_sent(message: Message, state: FSMContext):
    
    await state.update_data(code_not_sent_count=(await state.get_data()).get('code_not_sent_count', 0) + 1)
    if (await state.get_data()).get('code_not_sent_count', 0) >= 2:
        user_phone = (await state.get_data()).get('phone')
        await context.otp_service.send_otp(user_phone, OTP_CODE_LENGTH)
        await message.answer('Просим прощения за неудобство! Повторно отправляю код. Так же прошу перепроверить, правильно ли указан номер, на который зарегестрирован Ваш Whatsapp.', reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Код все еще не был отправлен')]], resize_keyboard=True))
        await state.set_state(RegistrationState.phone)
        return
    
    await message.answer('Давайте попробуем еще раз', reply_markup=ReplyKeyboardRemove())
    await handle_city_confirmation(message, state)
    
@router.message(RegistrationState.otp_code, F.text.len() != OTP_CODE_LENGTH)
async def handle_invalid_otp_code(message: Message, state: FSMContext):
    await message.reply('Это не похоже на 4-х значный код, попробуйте еще раз')
    await state.set_state(RegistrationState.otp_code)

@router.message(RegistrationState.otp_code, F.text.len() == OTP_CODE_LENGTH, F.text.func(str.isdigit))
async def handle_otp_code(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get('phone')
    
    response = await context.otp_service.verify_otp(phone, message.text)

    # Обработка ошибок верификации OTP
    error_messages = {
        'OTP has expired. Please request a new one.': (RegistrationState.request_otp_code, 'Код устарел, запросите новый код', kb.send_otp_code_reply_mu),
        'OTP has already been used.': (RegistrationState.request_otp_code, 'Код уже использован, запросите новый код', kb.send_otp_code_reply_mu),
        'Invalid OTP or phone number.': (RegistrationState.otp_code, 'Неверный код. Попробуйте еще раз', ReplyKeyboardRemove()),
    }

    if 'detail' in response:
        await state.update_data(wrong_otp_count=(await state.get_data()).get('wrong_otp_count', 0) + 1)
        if (await state.get_data()).get('wrong_otp_count', 0) >= 3:
            await message.answer('Вы превысили лимит попыток ввода кода. Запросите новый код через 5 минут.', reply_markup=kb.not_received_otp_code_reply_mu)
            await state.set_state(RegistrationState.request_otp_code)
            return
        state_target, error_msg, reply_markup = error_messages.get(response['detail'], (RegistrationState.phone, 'Ошибка при верификации кода'))
        await message.reply(error_msg, reply_markup=reply_markup)
        await state.set_state(state_target)
        return

    # Если OTP успешно подтвержден
    if response.get('message') == 'OTP verified successfully':
        try:
            user = crud.create_user(db, phone=phone, name=data.get('name'), city=data.get('city'))
            crud.set_user_id_for_tg_user(db, message.from_user.id, user.id)
            crud.create_session(db, user_id=user.id)
            sheets.record_add_user(user)
            
        except Exception as e:
            print(e)
            await message.reply('Ошибка при регистрации пользователя')
            await handle_back_start(message, state)
            return

        await state.clear()
        await handle_success_auth(message, state)
    else:
        await message.reply('Ошибка при обработке OTP. Попробуйте позже.')
        

