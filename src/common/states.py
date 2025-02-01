from aiogram.fsm.state import State, StatesGroup


class AppState(StatesGroup):
    initial = State()
    
class RegistrationState(StatesGroup):
    name = State()
    city = State()
    phone = State()

class LoginState(StatesGroup):
    pass