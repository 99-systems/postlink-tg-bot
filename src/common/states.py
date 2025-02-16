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

class LoginState(StatesGroup):
    phone = State()
    code = State()
    code_confirmation = State()

class SendParcelState(StatesGroup):
    from_city = State()
    from_city_confirmation = State()
    to_city = State()
    to_city_confirmation = State()
    parcel_description = State()
    parcel_weight = State()
    parcel_price = State()
    parcel_price_confirmation = State()
    # parcel_photo = State()