Ось оновлений `README.md` з урахуванням останніх змін та з інструкцією для створення файлів і папок:

```markdown
# AioHelp

AioHelp — це допоміжна бібліотека для роботи з [Aiogram](https://docs.aiogram.dev/), яка спрощує створення та налаштування Telegram-ботів.

## Основні можливості

- **Швидкий старт**: Бібліотека надає шаблони для запуску бота за кілька кроків.
- **Роутери та хендлери**: Простий спосіб обробки команд.
- **Генерація клавіатур**: Інструменти для створення клавіатур Telegram.
- **Middleware**: Легке налаштування проміжного програмного забезпечення.
- **Легка робота зі станами та локалізацією.**
- **Підтримка обробки зображень.**
- **Інструменти для роботи з базами даних.**

## Встановлення

1. Установіть бібліотеку за допомогою `pip`:
   ```bash
   pip install splaueef
   ```

2. Створіть структуру проекту:
   ```bash
   splaueef-init
   ```

   **Альтернатива**:
   Ви також можете створити файли вручну:
   ```bash
   python -m splaueef.utils init_project
   ```

## Використання

### Файл `config.py`

Додайте ваш токен у файл `config.py`:
```python
BOT_TOKEN = "your_telegram_bot_token"
```

### Хендлери

Бібліотека підтримує сучасний підхід **Aiogram 3.x**. У `handlers.py` додавайте обробку команд:
```python
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command(commands=["start"]))
async def start_command(message: types.Message):
    await message.answer("Привіт! Це твій бот.")
```

### Генерація клавіатур
```python
from splaueef.keyboards import generate_keyboard

keyboard = generate_keyboard([
    ["Кнопка 1", "Кнопка 2"],
    ["Кнопка 3"]
])
```

### Middleware
```python
from splaueef.middlewares import SimpleLoggingMiddleware

middleware = SimpleLoggingMiddleware()
```

### Робота зі станами
```python
from splaueef.states import BotStates

class MyStates(BotStates):
    START = "start"
    CONFIRM = "confirm"
```

### Робота з локалізацією
```python
from splaueef.localization import get_localized_message

message = get_localized_message("welcome", "uk")
```

### Обробка зображень
```python
from splaueef.image_processing import extract_text_from_image

text = extract_text_from_image("path/to/image.jpg")
```

### Робота з базами даних
```python
from splaueef.db_helpers import initialize_db

async def main():
    await initialize_db("my_database.db")
```

---

## Додаткові можливості

- **Автоматична структура проекту**: Команда `splaueef-init` створює структуру проекту.
- **Розширена підтримка баз даних.**
- **Інструменти для обробки зображень (розпізнавання тексту, QR-кодів).**

---

## Підтримка

Якщо у вас є питання чи пропозиції, звертайтеся:
- Telegram: [Група підтримки](https://t.me/+be4T9FkKBeczMzUy)

---

## Ліцензія

Цей проект розповсюджується за ліцензією **MIT**.
```

### Основні оновлення:
1. **Додано інструкцію з командами:**
   - Як встановити бібліотеку.
   - Як створити структуру проекту автоматично або вручну.

2. **Опис нових функцій:**
   - Робота зі станами, локалізацією, обробкою зображень і базами даних.

3. **Покращено опис для кінцевого користувача.**

4. **Підтримка зворотного зв’язку.**

Цей `README.md` забезпечить чітке розуміння можливостей бібліотеки та її встановлення! 🚀