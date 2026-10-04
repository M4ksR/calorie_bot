from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from states import CustomFood

router = Router()

@router.callback_query(F.data == "my_food")
async def my_food_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(CustomFood.waiting_for_name_of_food)
    await callback.message.answer("Введите название блюда:")

@router.message(CustomFood.waiting_for_name_of_food, F.text)
async def custom_food_name_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(food_name=message.text.strip())
    await state.set_state(CustomFood.waiting_for_kbju)
    await message.answer("Введите КБЖУ на 100г продукта\n"
                         "Например: 106 2 10 2\n"
                         "Что расшифровывается как\n"
                         "Калории - 106, Белки - 2, Жиры - 10, Углеводы - 2")

@router.message(CustomFood.waiting_for_kbju, F.text)
async def custom_food_kbju_handler(message: Message, state: FSMContext) -> None:
    values = message.text.split()
    if len(values) != 4:
        await message.answer("Неверный формат ввода")
        return

    try:
        calories, protein, fat, carbs = map(float, values)
    except ValueError:
        await message.answer("Неверный формат ввода")
        return

    if any(value < 0 for value in (calories, protein, fat, carbs)):
        await message.answer("Неверный формат")
        return

    await state.update_data(calories=calories,
                            protein=protein,
                            fat=fat,
                            carbs=carbs)

    await state.set_state(CustomFood.waiting_for_weight)
    await message.answer("Введите вес блюда")

@router.message(CustomFood.waiting_for_weight, F.text)
async def custom_food_weight_handler(message: Message, state: FSMContext) -> None:
    value = message.text.strip()
    try:
        value = float(value)
    except ValueError:
        await message.answer("Неверный формат")
        return

    if value <= 0:
        await message.answer("Неверный формат")
        return

    data = await state.get_data()

    await message.answer(f"Калории на {value}г: {data["calories"] * value / 100}\n"
                         f"Белки на {value}г: {data["protein"] * value / 100}\n"
                         f"Жиры на {value}г: {data["fat"] * value / 100}\n"
                         f"Углеводы на {value}г: {data["carbs"] * value / 100}")
    await state.clear()
