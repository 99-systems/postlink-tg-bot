from aiogram.fsm.state import State, StatesGroup


    
    
class SupportState(StatesGroup):
    user_type = State()
    problem = State()
    problem_description = State()
    request_no = State()
    confirmation = State()
    

