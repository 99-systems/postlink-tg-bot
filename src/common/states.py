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
    pass