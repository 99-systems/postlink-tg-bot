from aiogram.fsm.state import State, StatesGroup


class AppState(StatesGroup):
    initial = State()
    menu = State()
    
    
class SupportState(StatesGroup):
    initial = State()
    unknown_problem_description = State()
    
class RegistrationState(StatesGroup):
    name = State()
    city = State()
    city_confirmation = State()
    phone = State()
    otp_code = State()

class LoginState(StatesGroup):
    phone = State()
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