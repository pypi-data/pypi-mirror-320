from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import locale
import sys

# Примусово встановлюємо UTF-8 у Windows
if sys.platform == "win32":
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    os.environ["PYTHONUTF8"] = "1"

def create_project_structure():
    """Автоматично створює необхідні папки та файли."""
    folders = ["handlers", "middlewares", "keyboards", "states", "tests"]
    base_path = os.getcwd()

    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        # Додаємо __init__.py у кожну папку
        init_file = os.path.join(folder_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                f.write("# Цей файл визначає папку як пакет\n")

    # Створюємо базові файли
    files = {
        "bot.py": "# Базова конфігурація бота\n",
        "README.md": "# Проект AioHelp\n",
        "config.py": "# BOT_TOKEN = 'your_token_here'\n",
    }
    for file_name, content in files.items():
        file_path = os.path.join(base_path, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"File created: {file_path}")

# Клас для автоматичного створення структури
class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        print("Запускаємо створення структури проекту...")
        create_project_structure()
        print("Структура проекту успішно створена!")

setup(
    name="splaueef",
    version="0.1.5",
    packages=find_packages(),
    install_requires=["aiogram>=3.0", "certifi"],
    author="Splaueef",
    author_email="Splaueef@gmail.com",
    description="Допоміжна бібліотека для роботи з aiogram",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Splaueef/aiohelp.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    cmdclass={
        'install': CustomInstallCommand,
    },
)
