from aiogram.fsm.state import State, StatesGroup


class AppState(StatesGroup):
    terms = State()
    terms_declined = State()
    auth = State()
    menu = State()
    
    
class SupportState(StatesGroup):
    user_type = State()
    problem = State()
    problem_description = State()
    request_no = State()
    confirmation = State()
    
class RegistrationState(StatesGroup):
    name = State()
    city = State()
    city_confirmation = State()
    phone = State()
    request_otp_code = State()
    otp_code = State()

class LoginState(StatesGroup):
    phone = State()
    request_otp_code = State()
    otp_code = State()

class SendParcelState(StatesGroup):
    from_city = State()
    from_city_confirmation = State()
    to_city = State()
    to_city_confirmation = State()
    date_choose = State()
    date_confirmation = State()
    size_choose = State()
    size_confirmation = State()
    description = State()  
    # parcel_photo = State()

class DeliverParcelState(StatesGroup):
    from_city = State()
    from_city_confirmation = State()
    to_city = State()
    to_city_confirmation = State()
    date_choose = State()
    date_confirmation = State()
    size_choose = State()
    another_delivery_request = State()
    another_delivery_request_confirmation = State()