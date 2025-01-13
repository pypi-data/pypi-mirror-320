# handlers.py
from aiogram import Router, types
from aiogram.filters import Command

# Створюємо роутер для реєстрації хендлерів
router = Router()

@router.message(Command(commands=["start"]))
async def start_command(message: types.Message):
    """Обробляє команду /start."""
    await message.answer("Вітаємо! Це базова конфігурація бота AioHelp.")

@router.message(Command(commands=["help"]))
async def help_command(message: types.Message):
    """Обробляє команду /help."""
    await message.answer("Доступні команди:\n/start - Почати\n/help - Допомога")