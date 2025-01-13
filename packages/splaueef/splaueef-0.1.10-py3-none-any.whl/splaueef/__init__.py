from .bot_config import create_bot_and_dispatcher
from .handlers import router
from .tools import create_project_structure
from .keyboards import create_reply_keyboard, create_inline_keyboard
from .command_helpers import add_text_command, add_button_command, add_file_command, add_image_command
from aiogram.types import Message
from unittest.mock import AsyncMock
from .error_handling import ErrorLoggingMiddleware
from .state_helpers import set_state_data, get_state_data
from .menu_helpers import create_menu
from .cache import LocalCache
from .response_templates import render_template
from .test_helpers import create_fake_message







def init_project():
    create_project_structure()
    print("Структура проекту успішно створена!")
