from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def create_reply_keyboard(buttons: list[list[str]], resize: bool = True, one_time: bool = False) -> ReplyKeyboardMarkup:
    """
    Створює Reply клавіатуру (звичайну клавіатуру).
    
    Args:
        buttons (list[list[str]]): Двовимірний список тексту кнопок.
        resize (bool): Зменшення розміру кнопок (за замовчуванням True).
        one_time (bool): Одноразова клавіатура (зникає після натискання).
    
    Returns:
        ReplyKeyboardMarkup: Згенерована клавіатура.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=resize, one_time_keyboard=one_time)
    for row in buttons:
        keyboard.row(*[KeyboardButton(text) for text in row])
    return keyboard


def create_inline_keyboard(buttons: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    """
    Створює Inline клавіатуру (інлайн-клавіатуру).
    
    Args:
        buttons (list[list[tuple[str, str]]]): Двовимірний список (текст кнопки, callback_data).
    
    Returns:
        InlineKeyboardMarkup: Згенерована клавіатура.
    """
    keyboard = InlineKeyboardMarkup()
    for row in buttons:
        keyboard.row(*[InlineKeyboardButton(text, callback_data=data) for text, data in row])
    return keyboard
