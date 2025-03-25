from aiogram.filters.callback_data import CallbackData
from enum import Enum

class User(str, Enum):
    sender = 'sender'
    delivery = 'delivery'

class Action(str, Enum):
    accept = 'accept'
    reject = 'reject'

class RequestCallback(CallbackData, prefix='request'):
    user: User
    action: Action
    send_request_id: int
    delivery_request_id: int
    sending_user_id: int
    delivering_user_id: int