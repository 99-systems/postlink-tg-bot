from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder 


start_kb = [[KeyboardButton(text='Регистрация')], [KeyboardButton(text='Логин')]]
start_reply_mu = ReplyKeyboardMarkup(keyboard=start_kb, resize_keyboard=True)


auth_back_kb = [[KeyboardButton(text='Назад')]]
auth_back_reply_mu = ReplyKeyboardMarkup(keyboard=auth_back_kb, is_persistent=False, resize_keyboard=True)


city_conf_kb = [[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]]
city_conf_reply_mu = ReplyKeyboardMarkup(keyboard=city_conf_kb, resize_keyboard=True)


phone_kb = [[KeyboardButton(text='Отправить номер телефона', request_contact=True)]]
phone_reply_mu = ReplyKeyboardMarkup(keyboard=phone_kb, resize_keyboard=True)

main_menu_kb = [[KeyboardButton(text='Отправить посылку'),
                  KeyboardButton(text='Доставить посылку')], 
                  [KeyboardButton(text='Служба поддержки')],
                [KeyboardButton(text='Краткая инструкция'), KeyboardButton(text='Выход')]] 
main_menu_reply_mu = ReplyKeyboardMarkup(keyboard=main_menu_kb, resize_keyboard=True)

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

