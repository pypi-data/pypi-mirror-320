# localization.py

# Словник для зберігання вибору мови користувачів
user_languages = {}

translations = {
    "uk": {"greeting": "Вітаю!"},
    "en": {"greeting": "Hello!"},
}

def set_language(user_id: int, language: str):
    """
    Встановлює мову для користувача.
    
    Args:
        user_id (int): Унікальний ідентифікатор користувача.
        language (str): Код мови (наприклад, "uk", "en").
    """
    user_languages[user_id] = language

def get_translation(key: str, language: str):
    """
    Повертає переклад для ключа і мови.
    
    Args:
        key (str): Ключ для перекладу.
        language (str): Код мови.

    Returns:
        str: Переклад, якщо він знайдений, інакше ключ.
    """
    return translations.get(language, {}).get(key, key)
