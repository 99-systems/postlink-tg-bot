import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from src.utils import generate_excel_file
from src.common.keyboard import admin_menu_kb
from src.middlewares.check_admin_middleware import AdminOnlyMiddleware

router = Router()

router.message.middleware(AdminOnlyMiddleware())

@router.message(Command("admin"))
async def admin_menu(message: Message):
    await message.answer("Добро пожаловать в админ-меню.", reply_markup=admin_menu_kb)

@router.message(F.text.lower() == "экспорт данных")
async def export_requests(message: Message):
    filenames = generate_excel_file()

    if not filenames:
        await message.answer("Нет данных для экспорта.")
        return

    for filename in filenames:
        file = FSInputFile(filename)
        await message.answer_document(file)
        os.remove(filename) 


@router.message(F.text.lower() == "онлайн таблица")
async def export_requests(message: Message):
    filenames = generate_excel_file()

    if not filenames:
        await message.answer("Нет данных для экспорта.")
        return

    for filename in filenames:
        file = FSInputFile(filename)
        await message.answer_document(file)
        os.remove(filename) 
