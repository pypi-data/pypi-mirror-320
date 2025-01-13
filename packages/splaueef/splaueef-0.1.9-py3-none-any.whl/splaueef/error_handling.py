from aiogram.types import Update
from aiogram.dispatcher.middlewares.base import BaseMiddleware
import logging

class ErrorLoggingMiddleware(BaseMiddleware):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids
        super().__init__()

    async def on_pre_process_update(self, update: Update, data: dict):
        try:
            await super().on_pre_process_update(update, data)
        except Exception as e:
            logging.error(f"Помилка: {e}")
            if self.admin_ids:
                for admin_id in self.admin_ids:
                    await update.bot.send_message(admin_id, f"⚠️ Помилка: {e}")
