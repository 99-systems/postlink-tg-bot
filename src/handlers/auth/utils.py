def format_phone_number(phone_number: str) -> str:
    phone_number = phone_number.replace(' ', '').replace('+', '').replace('-', '')
    return phone_number


