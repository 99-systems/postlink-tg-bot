from aiogram.filters.callback_data import CallbackData
from enum import Enum
from dataclasses import dataclass, asdict

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
    
    def to_dict(self):
        return {
            "user": self.user.value,
            "action": self.action.value,
            "send_request_id": self.send_request_id,
            "delivery_request_id": self.delivery_request_id,
            "sending_user_id": self.sending_user_id,
            "delivering_user_id": self.delivering_user_id,
        }
    