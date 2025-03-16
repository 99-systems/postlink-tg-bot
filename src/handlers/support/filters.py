from aiogram.filters import Filter
from aiogram.types import Message

from .base import support_problems


class KnownProblemFilter(Filter):
    
    def __init__(self):
        self.problems = [str(problem) for problem in support_problems]
    
        
    async def __call__(self, message: Message):
        return message.text.lower() in self.problems
    
class UnkownProblemFilter(Filter):
    
    def __init__(self):
        self.problems = [str(problem) for problem in support_problems]
    
    async def __call__(self, message: Message):
        return message.text.lower() not in self.problems