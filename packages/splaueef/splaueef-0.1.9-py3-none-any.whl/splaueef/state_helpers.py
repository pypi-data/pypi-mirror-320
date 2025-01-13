from aiogram.fsm.context import FSMContext

async def set_state_data(state: FSMContext, key: str, value):
    """Зберігає дані у стан."""
    data = await state.get_data()
    data[key] = value
    await state.set_data(data)

async def get_state_data(state: FSMContext, key: str):
    """Отримує дані з стану."""
    data = await state.get_data()
    return data.get(key)
