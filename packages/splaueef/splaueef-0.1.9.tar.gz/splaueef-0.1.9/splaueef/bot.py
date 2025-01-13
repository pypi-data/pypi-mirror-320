import asyncio
import logging
from splaueef.bot_config import create_bot_and_dispatcher
from splaueef.handlers import router  # Імпортуємо роутер

async def main():
    """
    Основна функція для запуску бота.
    """
    logging.basicConfig(level=logging.INFO)
    logging.info("Запускаємо бота...")

    bot, dp = create_bot_and_dispatcher("YOUR_BOT_TOKEN")
    dp.include_router(router)  # Додаємо роутер із командами

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот зупинено.")