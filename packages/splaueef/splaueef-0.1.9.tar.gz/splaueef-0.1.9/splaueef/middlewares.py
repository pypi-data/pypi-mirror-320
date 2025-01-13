from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def generate_keyboard(buttons: list[list[str]]) -> ReplyKeyboardMarkup:
    """
    Генерує клавіатуру на основі списку кнопок.

    Args:
        buttons (list[list[str]]): Список кнопок у вигляді двовимірного масиву.

    Returns:
        ReplyKeyboardMarkup: Згенерована клавіатура.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for row in buttons:
        keyboard.row(*[KeyboardButton(text) for text in row])
    return keyboard
