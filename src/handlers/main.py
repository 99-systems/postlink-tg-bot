from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from src.common.states import AppState, RegistrationState
from src.common import keyboard as kb


router = Router()
