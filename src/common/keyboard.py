from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.handlers.support import support_problems
from src.database.models import crud
from src.database.models.request import DeliveryRequest, SendRequest
from src.database import db

not_received_otp_code_kb = [[KeyboardButton(text='Код не был отправлен')]]
not_received_otp_code_reply_mu = ReplyKeyboardMarkup(keyboard=not_received_otp_code_kb, resize_keyboard=True)

send_otp_code_kb = [[KeyboardButton(text='Отправить код')]]
send_otp_code_reply_mu = ReplyKeyboardMarkup(keyboard=send_otp_code_kb, resize_keyboard=True)

confirmation_kb = [[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]]
confirmation_reply_mu = ReplyKeyboardMarkup(keyboard=confirmation_kb, resize_keyboard=True)

user_type_kb = [[KeyboardButton(text='Отправитель'), KeyboardButton(text='Курьер'), KeyboardButton(text='Новый пользователь')]]
user_type_reply_mu = ReplyKeyboardMarkup(keyboard=user_type_kb, resize_keyboard=True)

auth_kb = [[KeyboardButton(text='Регистрация')], [KeyboardButton(text='Авторизация')]]
auth_reply_mu = ReplyKeyboardMarkup(keyboard=auth_kb, resize_keyboard=True)


terms_kb = [[KeyboardButton(text='Согласен')], [KeyboardButton(text='Не согласен')]]
terms_reply_mu = ReplyKeyboardMarkup(keyboard=terms_kb, resize_keyboard=True)

open_terms_kb = [[KeyboardButton(text='Открыть Пользовательское Соглашение и Политику конфиденциальности')]]
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


def create_main_menu_markup(tg_id: str):
    open_request = crud.get_open_request(db, tg_id=tg_id)
    keyboard = []
    if open_request is None:
        keyboard.append([KeyboardButton(text='Хочу отправить посылку'), KeyboardButton(text='Хочу доставить посылку')])
    else:
        
        if isinstance(open_request, SendRequest):
            keyboard.append([KeyboardButton(text='Статус заявки'), KeyboardButton(text='Отменить заявку')])
        if isinstance(open_request, DeliveryRequest):
            delivery_requests = crud.get_all_open_delivery_requests_by_tg_id(db, tg_id)
            if len(delivery_requests) == 1:
                keyboard.append([KeyboardButton(text='Статус заявки'), KeyboardButton(text='Отменить заявку'), KeyboardButton(text='Создать еще одну заявку')])
            else:
                keyboard.append([KeyboardButton(text='Статус заявок'), KeyboardButton(text='Отменить заявку')])

    keyboard.append([KeyboardButton(text='Безопасность Отправителей'), KeyboardButton(text='Безопасность Курьеров')])
    keyboard.append([KeyboardButton(text='Служба поддержки')])
    keyboard.append([KeyboardButton(text='Выход')])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

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
sizes_kb_builder.row(InlineKeyboardButton(text='Маленькая – до 2 кг, до 30 см по каждой стороне', callback_data=f'size:small'))
sizes_kb_builder.row(InlineKeyboardButton(text='Средняя – до 15 кг, до 60 см по каждой стороне', callback_data=f'size:medium'))
sizes_kb_builder.row(InlineKeyboardButton(text='Большая – до 30 кг, до 100 см по каждой стороне', callback_data=f'size:large'))
sizes_kb_builder.row(InlineKeyboardButton(text='Крупногабаритная – более 30 кг, более 100 см по одной из сторон', callback_data=f'size:extra_large'))
sizes_kb = sizes_kb_builder.as_markup()

sizes_kb_builder.row(InlineKeyboardButton(text='Любую из вышеперечисленных', callback_data=f'size:skip'))
sizes_kb_del = sizes_kb_builder.as_markup()

no_desc = [[KeyboardButton(text='Пропустить')]]
no_desc_kb = ReplyKeyboardMarkup(keyboard=no_desc, resize_keyboard=True)


from src.handlers.request.callbacks import RequestCallback, Action, User

def create_accept_buttons_for_sender(send_req_id: int, delivery_req_id: int, sending_user_id: int, delivering_user_id: int):
    inl_builder = InlineKeyboardBuilder()
    inl_builder.row(
        InlineKeyboardButton(
            text='Принять✅',
            callback_data=RequestCallback(
                user=User.sender,
                action=Action.accept,
                send_request_id=send_req_id,
                delivery_request_id=delivery_req_id,
                sending_user_id=sending_user_id,
                delivering_user_id=delivering_user_id
            ).pack()
        ),
        InlineKeyboardButton(
            text='Отклонить❌',
            callback_data=RequestCallback(
                user=User.sender,
                action=Action.reject,
                send_request_id=send_req_id,
                delivery_request_id=delivery_req_id,
                sending_user_id=sending_user_id,
                delivering_user_id=delivering_user_id
            ).pack()
        )
    )
    return inl_builder.as_markup()


def create_accept_buttons_for_delivery(send_req_id: int, delivery_req_id: int, sending_user_id: int, delivering_user_id: int):
    inl_builder = InlineKeyboardBuilder()
    inl_builder.row(
        InlineKeyboardButton(
            text='Принять✅',
            callback_data=RequestCallback(
                user=User.delivery,
                action=Action.accept,
                send_request_id=send_req_id,
                delivery_request_id=delivery_req_id,
                sending_user_id=sending_user_id,
                delivering_user_id=delivering_user_id
            ).pack()
        ),
        InlineKeyboardButton(
            text='Отклонить❌',
            callback_data=RequestCallback(
                user=User.delivery,
                action=Action.reject,
                send_request_id=send_req_id,
                delivery_request_id=delivery_req_id,
                sending_user_id=sending_user_id,
                delivering_user_id=delivering_user_id
            ).pack()
        )
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