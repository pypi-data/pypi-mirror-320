from aiogram import Bot, Dispatcher
import ssl
import certifi

def create_bot_and_dispatcher(token: str):
    """
    Ініціалізує бот і диспетчер.
    Args:
        token (str): Токен Telegram бота.
    Returns:
        Tuple[Bot, Dispatcher]: Об'єкти бота та диспетчера.
    """
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    bot = Bot(token=token, session_params={"connector_args": {"ssl": ssl_context}})
    dp = Dispatcher()
    return bot, dp