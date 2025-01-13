import unittest
from splaueef.bot import AioBot

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import ssl
import certifi

class AioBot:
    def __init__(self, token: str):
        """
        Ініціалізує бота та диспетчер.
        Args:
            token (str): Токен Telegram бота.
        """
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.bot = Bot(token=token, session_params={"connector_args": {"ssl": ssl_context}})
        self.dispatcher = Dispatcher(storage=MemoryStorage())

    def get_bot(self):
        """Повертає об'єкт бота."""
        return self.bot

    def get_dispatcher(self):
        """Повертає об'єкт диспетчера."""
        return self.dispatcher
