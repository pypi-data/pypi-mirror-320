from .bot_config import create_bot_and_dispatcher
from .handlers import router
def init_project():
    from .setup import create_project_structure
    create_project_structure()
    print("Структура проекту успішно створена!")
