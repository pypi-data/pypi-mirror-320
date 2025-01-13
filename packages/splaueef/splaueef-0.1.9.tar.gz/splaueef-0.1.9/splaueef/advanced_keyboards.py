# advanced_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_dynamic_keyboard(data: list[dict], callback_prefix: str):
    keyboard = InlineKeyboardMarkup()
    for item in data:
        keyboard.add(InlineKeyboardButton(text=item["label"], callback_data=f"{callback_prefix}:{item['id']}"))
    return keyboard

def create_pagination_keyboard(page: int, total_pages: int):
    keyboard = InlineKeyboardMarkup()
    if page > 1:
        keyboard.add(InlineKeyboardButton(text="⬅️ Попередня", callback_data=f"page:{page - 1}"))
    if page < total_pages:
        keyboard.add(InlineKeyboardButton(text="➡️ Наступна", callback_data=f"page:{page + 1}"))
    return keyboard
