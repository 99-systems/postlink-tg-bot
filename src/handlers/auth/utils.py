def format_phone_number(phone_number: str) -> str:
    # Change the first character to '7' if it is '8'
    if phone_number.startswith('8'):
        phone_number = '7' + phone_number[1:]
    phone_number = phone_number.replace(' ', '').replace('+', '').replace('-', '')
    return phone_number


