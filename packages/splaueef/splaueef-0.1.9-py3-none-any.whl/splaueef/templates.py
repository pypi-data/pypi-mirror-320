# templates.py
from aiogram import Router
from aiogram.types import Message

def faq_template(questions_answers: dict):
    router = Router()

    @router.message()
    async def handle_faq(message: Message):
        question = message.text.strip().lower()
        answer = questions_answers.get(question, "Вибачте, я не знаю відповіді на це питання.")
        await message.answer(answer)

    return router
