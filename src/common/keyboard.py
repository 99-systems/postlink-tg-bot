
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder 



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