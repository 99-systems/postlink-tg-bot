from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder 

from src.handlers.support import support_problems

confirmation_kb = [[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]]
confirmation_reply_mu = ReplyKeyboardMarkup(keyboard=confirmation_kb, resize_keyboard=True)

user_type_kb = [[KeyboardButton(text='Отправитель'), KeyboardButton(text='Курьер')]]
user_type_reply_mu = ReplyKeyboardMarkup(keyboard=user_type_kb, resize_keyboard=True)

auth_kb = [[KeyboardButton(text='Регистрация')], [KeyboardButton(text='Авторизация')]]
auth_reply_mu = ReplyKeyboardMarkup(keyboard=auth_kb, resize_keyboard=True)


terms_kb = [[KeyboardButton(text='Согласен')], [KeyboardButton(text='Не согласен')]]
terms_reply_mu = ReplyKeyboardMarkup(keyboard=terms_kb, resize_keyboard=True)

open_terms_kb = [[KeyboardButton(text='Открыть пользовательское соглашение')]]
open_terms_reply_mu = ReplyKeyboardMarkup(keyboard=open_terms_kb, resize_keyboard=True)

back_kb = [[KeyboardButton(text='Назад')]]
back_reply_mu = ReplyKeyboardMarkup(keyboard=back_kb, is_persistent=False, resize_keyboard=True)


city_conf_kb = [[KeyboardButton(text='Да'), KeyboardButton(text='Неверный адрес')]]
city_conf_reply_mu = ReplyKeyboardMarkup(keyboard=city_conf_kb, resize_keyboard=True)


request_location_kb = [[KeyboardButton(text='Отправить местоположение', request_location=True)]]
request_location_reply_mu = ReplyKeyboardMarkup(keyboard=request_location_kb, resize_keyboard=True)

request_location_and_back_reply_mu = ReplyKeyboardMarkup(keyboard=[request_location_kb[0], back_kb[0]], resize_keyboard=True)

phone_kb = [[KeyboardButton(text='Поделиться контактом с ботом', request_contact=True)]]
phone_reply_mu = ReplyKeyboardMarkup(keyboard=phone_kb, resize_keyboard=True)

main_menu_kb = [
    [KeyboardButton(text='Хочу отправить посылку'), KeyboardButton(text='Хочу доставить посылку')], 
    [KeyboardButton(text='Безопасность Отправителей'), KeyboardButton(text='Безопасность Курьеров')],
    [KeyboardButton(text='Служба поддержки')],
    [KeyboardButton(text='Выход')]
    ] 
main_menu_reply_mu = ReplyKeyboardMarkup(keyboard=main_menu_kb, resize_keyboard=True)

main_menu_open_req_kb = [
    [KeyboardButton(text='Статус заявки'), KeyboardButton(text='Отменить заявку')], 
    [KeyboardButton(text='Безопасность Отправителей'), KeyboardButton(text='Безопасность Курьеров')],
    [KeyboardButton(text='Служба поддержки')],
    [KeyboardButton(text='Выход')]
    ] 
main_menu_open_req_reply_mu = ReplyKeyboardMarkup(keyboard=main_menu_open_req_kb, resize_keyboard=True)

support_problems_kb = [[KeyboardButton(text=problem.name)] for problem in support_problems]
support_problems_reply_mu = ReplyKeyboardMarkup(keyboard=support_problems_kb, resize_keyboard=True)

test_b = InlineKeyboardBuilder()
test_b.row(InlineKeyboardButton(text='Принять', callback_data=f'test'),InlineKeyboardButton(text='Отклонить', callback_data=f'test'))
test_mk = test_b.as_markup()

def create_to_curr_city_mu(city: str):
    inl_builder = InlineKeyboardBuilder()
    inl_builder.row(InlineKeyboardButton(text=city, callback_data=f'to_city:current'))
    return inl_builder.as_markup()

def create_from_curr_city_mu(city: str):
    inl_builder = InlineKeyboardBuilder()
    inl_builder.row(InlineKeyboardButton(text=city, callback_data=f'from_city:current'))
    return inl_builder.as_markup()


sizes_kb_builder  = InlineKeyboardBuilder()
sizes_kb_builder.row(InlineKeyboardButton(text='Маленькая – до 1 кг, до 20 см по каждой стороне', callback_data=f'size:small'))
sizes_kb_builder.row(InlineKeyboardButton(text='Средняя – до 5 кг, до 35 см по каждой стороне', callback_data=f'size:medium'))
sizes_kb_builder.row(InlineKeyboardButton(text='Большая – до 10 кг, до 50 см по каждой стороне', callback_data=f'size:large'))
sizes_kb_builder.row(InlineKeyboardButton(text='Крупногабаритная – более 10 кг, более 50 см по одной из сторон', callback_data=f'size:extra_large'))
sizes_kb = sizes_kb_builder.as_markup()

sizes_kb_builder.row(InlineKeyboardButton(text='Пропустить', callback_data=f'size:skip'))
sizes_kb_del = sizes_kb_builder.as_markup()

no_desc = [[KeyboardButton(text='Пропустить')]]
no_desc_kb = ReplyKeyboardMarkup(keyboard=no_desc, resize_keyboard=True)

def create_send_req_buttons(send_req_id: int):
    inl_builder = InlineKeyboardBuilder()
    inl_builder.row(
        InlineKeyboardButton(text='Принять✅', callback_data=f'accept_req:{send_req_id}'),
        InlineKeyboardButton(text='Отклонить❌', callback_data=f'reject_req:{send_req_id}')
    )
    return inl_builder.as_markup()


def create_close_req_button(req_type: str, req_id: int):
    inl_builder = InlineKeyboardBuilder()
    inl_builder.row(InlineKeyboardButton(text='Закрыть заявку', callback_data=f'close_req:{req_type}:{req_id}'))
    return inl_builder.as_markup()

admin_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Экспорт данных")]],
    resize_keyboard=True
)