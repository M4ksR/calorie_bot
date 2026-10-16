from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from states import CustomFood
from keyboards import confirm_custom_food, add_food_menu, start_menu, cancel_add_food, go_to_start_menu
from database import save_food, add_food_and_update_streak

router = Router()

@router.callback_query(F.data == "my_food")
async def my_food_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(CustomFood.waiting_for_name_of_food)
    await callback.message.edit_text("Введите название блюда:", reply_markup=cancel_add_food())

@router.message(CustomFood.waiting_for_name_of_food, F.text)
async def custom_food_name_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(food_name=message.text.strip())
    await state.set_state(CustomFood.waiting_for_kbju)
    await message.answer("Введите КБЖУ на 100г продукта\n"
                         "Например: 106 2 10 2\n"
                         "Что расшифровывается как\n"
                         "Калории - 106, Белки - 2, Жиры - 10, Углеводы - 2", reply_markup=cancel_add_food())

@router.message(CustomFood.waiting_for_kbju, F.text)
async def custom_food_kbju_handler(message: Message, state: FSMContext) -> None:
    values = message.text.split()
    if len(values) != 4:
        await message.answer("Неверный формат ввода", reply_markup=go_to_start_menu())
        return

    try:
        calories, protein, fat, carbs = map(float, values)
    except ValueError:
        await message.answer("Неверный формат ввода", reply_markup=go_to_start_menu())
        return

    if any(value < 0 for value in (calories, protein, fat, carbs)):
        await message.answer("Неверный формат", reply_markup=go_to_start_menu())
        return

    await state.update_data(calories=calories,
                            protein=protein,
                            fat=fat,
                            carbs=carbs)

    await state.set_state(CustomFood.waiting_for_weight)
    await message.answer("Введите вес блюда", reply_markup=cancel_add_food())

@router.message(CustomFood.waiting_for_weight, F.text)
async def custom_food_weight_handler(message: Message, state: FSMContext) -> None:
    value = message.text.strip()
    try:
        value = float(value.replace(',','.'))
    except ValueError:
        await message.answer("Неверный формат", reply_markup=go_to_start_menu())
        return

    if value <= 0:
        await message.answer("Неверный формат", reply_markup=go_to_start_menu())
        return

    await state.update_data(weight=value)
    data = await state.get_data()

    await message.answer(f"Название блюда: {data['food_name']}\n\n"
                         f"КБЖУ на {int(value) if value == int(value) else value}г:\n\n"
                         f"К:  {data['calories'] * value / 100:.1f}\n"
                         f"Б:  {data['protein'] * value / 100:.1f}\n"
                         f"Ж:  {data['fat'] * value / 100:.1f}\n"
                         f"У:  {data['carbs'] * value / 100:.1f}",
                         reply_markup=confirm_custom_food())

@router.callback_query(F.data.in_({"confirm_food", "confirm_and_save_food"}))
async def confirm_food_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    coef =  data['weight'] / 100
    await add_food_and_update_streak(callback.from_user.id,
                         data['food_name'],
                         data['weight'],
                         data['calories'] * coef,
                         data['protein'] * coef,
                         data['fat'] * coef,
                         data['carbs'] * coef)

    if callback.data == "confirm_and_save_food":
        await save_food(callback.from_user.id,
                        data['food_name'],
                        data['calories'],
                        data['protein'],
                        data['fat'],
                        data['carbs'])

    await callback.message.edit_text(f"Блюдо {data['food_name']} добавлено\n\n"
                                    f"Calorie Counter",
                                    reply_markup=start_menu())
    await state.clear()

@router.callback_query(F.data == "cancel_food")
async def cancel_food_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.edit_text("Добавление отменено", reply_markup=add_food_menu())
    await state.clear()
