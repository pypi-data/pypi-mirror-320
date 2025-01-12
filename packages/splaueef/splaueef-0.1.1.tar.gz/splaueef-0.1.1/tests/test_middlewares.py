import unittest
from aiohelp.middlewares import SimpleLoggingMiddleware
from aiogram.types import Update

class TestMiddlewares(unittest.TestCase):
    async def test_logging_middleware(self):
        middleware = SimpleLoggingMiddleware()
        update = Update(update_id=1)
        # Test middleware functionality (mock actual calls if needed)
        await middleware.on_pre_process_update(update, {})
