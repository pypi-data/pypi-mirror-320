from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_menu(buttons: dict) -> InlineKeyboardMarkup:
    """
    Створює меню з кнопок.

    Args:
        buttons (dict): Ключі - текст кнопок, значення - callback_data.

    Returns:
        InlineKeyboardMarkup: Меню.
    """
    markup = InlineKeyboardMarkup()
    for text, callback_data in buttons.items():
        markup.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    return markup
