from .bot_config import create_bot_and_dispatcher
from .handlers import router
from .tools import create_project_structure

def init_project():
    create_project_structure()
    print("Структура проекту успішно створена!")
