import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from src.common.generate_excel import generate_excel_file
from src.common.keyboard import admin_menu_kb
from src.database.connection import db
from src.database.models import crud
from src.middlewares.check_admin_middleware import AdminOnlyMiddleware

router = Router()

router.message.middleware(AdminOnlyMiddleware())

@router.message(Command("admin"))
async def admin_menu(message: Message):
    user = crud.get_user_by_tg_id(db, message.from_user.id)
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