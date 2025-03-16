from aiogram.filters import Filter
from aiogram.types import Message

from .utils import format_phone_number


class PhoneNumberFilter(Filter):
    async def __call__(self, message: Message):
        
        if message.contact and message.contact.phone_number:
            return True
        
        # Examples of valid phone numbers:
        # +7 777 777 77 77
        # 8 777 777 77 77
        # 7 777 777 77 77
        # 77777777777
        # +77777777777
        # 87777777777
        
        phone_number = format_phone_number(message.text)
        if len(phone_number) == 11 and phone_number.isdigit():
            return True
        
        return False