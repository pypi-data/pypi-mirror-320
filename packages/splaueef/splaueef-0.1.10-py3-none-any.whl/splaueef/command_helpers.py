from aiogram import Router, types
from aiogram.types import InputFile, ReplyKeyboardMarkup, InlineKeyboardMarkup
from typing import Optional, Union

def add_text_command(router: Router, command: str, response: str):
    """
    Додає просту текстову команду до бота.

    Args:
        router (Router): Роутер для реєстрації команди.
        command (str): Назва команди (без '/').
        response (str): Відповідь на команду.
    """
    @router.message(commands=[command])
    async def text_command_handler(message: types.Message):
        await message.answer(response)

def add_button_command(router: Router, command: str, response: str, keyboard: Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]):
    """
    Додає команду з клавіатурою.

    Args:
        router (Router): Роутер для реєстрації команди.
        command (str): Назва команди (без '/').
        response (str): Відповідь на команду.
        keyboard (Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]): Клавіатура.
    """
    @router.message(commands=[command])
    async def button_command_handler(message: types.Message):
        await message.answer(response, reply_markup=keyboard)

def add_file_command(router: Router, command: str, file_path: str, caption: Optional[str] = None):
    """
    Додає команду для відправки файлу.

    Args:
        router (Router): Роутер для реєстрації команди.
        command (str): Назва команди (без '/').
        file_path (str): Шлях до файлу.
        caption (Optional[str]): Підпис до файлу.
    """
    @router.message(commands=[command])
    async def file_command_handler(message: types.Message):
        file = InputFile(file_path)
        await message.answer_document(file, caption=caption)

def add_image_command(router: Router, command: str, image_path: str, caption: Optional[str] = None):
    """
    Додає команду для відправки зображення.

    Args:
        router (Router): Роутер для реєстрації команди.
        command (str): Назва команди (без '/').
        image_path (str): Шлях до зображення.
        caption (Optional[str]): Підпис до зображення.
    """
    @router.message(commands=[command])
    async def image_command_handler(message: types.Message):
        image = InputFile(image_path)
        await message.answer_photo(image, caption=caption)
