from aiogram.filters.callback_data import CallbackData
from enum import Enum
from dataclasses import asdict

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
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            user=User(data["user"]),
            action=Action(data["action"]),
            send_request_id=data["send_request_id"],
            delivery_request_id=data["delivery_request_id"],
            sending_user_id=data["sending_user_id"],
            delivering_user_id=data["delivering_user_id"],
        )