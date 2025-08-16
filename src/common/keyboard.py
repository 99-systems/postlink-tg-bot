from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.handlers.support.base import support_problems


user_type_kb = [[KeyboardButton(text='Отправитель'), KeyboardButton(text='Курьер'), KeyboardButton(text='Новый пользователь')]]
user_type_reply_mu = ReplyKeyboardMarkup(keyboard=user_type_kb, resize_keyboard=True)




support_problems_kb = [[KeyboardButton(text=problem.name)] for problem in support_problems]
support_problems_reply_mu = ReplyKeyboardMarkup(keyboard=support_problems_kb, resize_keyboard=True)


admin_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Экспорт данных")]],
    resize_keyboard=True
)