from aiogram.types import Message
from unittest.mock import AsyncMock

def create_fake_message(text: str, user_id: int = 123456) -> Message:
    return Message(message_id=1, from_user={"id": user_id}, text=text)
