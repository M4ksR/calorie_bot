from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from states import AiFood
from aiogram.fsm.context import FSMContext
from keyboards import cancel_add_food, confirm_aifood, add_food_menu
from services.gemini import estimate_foods
from database import add_food_and_update_streak

router = Router()

@router.callback_query(F.data == "quick_calculation")
async def quick_calculation_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AiFood.waiting_for_food_list)
    await callback.message.edit_text("Введите название продукта и вес в граммах в следующем формате:\n"
                                     "<pre>Название - Вес</pre>\n\n"
                                     "Пример:\n"
                                     "<pre>Салат оливье перекресток - 250\n"
                                     "Куриная грудка вареная - 120</pre>",
                                     parse_mode="HTML",
                                     reply_markup=cancel_add_food())

@router.message(AiFood.waiting_for_food_list, F.text)
async def quick_food_list_handler(message: Message, state: FSMContext):
    menu = message.text.split('\n')
    foods = []
    for food in menu:
        try:
            split = food.rsplit(' - ', 1)
            food_name = split[0].strip()
            weight = float(split[1].replace(',','.').replace('г', '').strip())
            if food_name and weight > 0:
                foods.append({
                        'name': food_name,
                        'weight': weight
                    })
        except (ValueError, IndexError):
            foods = []
            break

    if not foods:
        await message.answer("Не удалось добавить продукты. Проверьте правильность написания",
                             reply_markup=cancel_add_food())
        return

    result = await estimate_foods(foods)
    if not result or len(result) != len(foods):
        await message.answer("Не удалось добавить продукты. Проверьте правильность написания",
                             reply_markup=cancel_add_food())

    estimated_foods = []
    for i in range(len(foods)):
        estimated_foods.append({
            "name": foods[i]['name'],
            "weight": foods[i]['weight'],
            "calories": result[i]['calories'],
            "protein": result[i]['protein'],
            "fat": result[i]['fat'],
            "carbs": result[i]['carbs']
        })

    await state.update_data(estimated_foods=estimated_foods)
    await state.set_state(AiFood.waiting_for_confirm)

    text = []
    for food in estimated_foods:
        text.append(f"{food['name']} - {food['weight']}\n"
                      f"<pre>"
                      f"{'Калории':<10}"
                      f"{'Белки':<9}"
                      f"{'Жиры':<8}"
                      f"{'Углеводы':<10}\n"
                      f"{food['calories']:<10.1f}"
                      f"{food['protein']:<9.1f}"
                      f"{food['fat']:<8.1f}"
                      f"{food['carbs']:<10.1f}"
                      f"</pre>\n\n")

    await message.answer("⚡Быстрый подсчет:\n\n"
                         f"{''.join(text)}"
                         f"⚠️ Значения приблизительные",
                         parse_mode="HTML",
                         reply_markup=confirm_aifood())

@router.callback_query(AiFood.waiting_for_confirm, F.data == "confirm_aifood")
async def confirm_aifood_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    estimated_foods = data['estimated_foods']

    for food in estimated_foods:
        await add_food_and_update_streak(callback.from_user.id,
                            food['name'],
                            food['weight'],
                            food['calories'],
                            food['protein'],
                            food['fat'],
                            food['carbs'])

    await state.clear()
    await callback.message.edit_text("Еда успешно добавлена\n\n"
                                     "Добавление еды:",
                                     reply_markup=add_food_menu())

@router.callback_query(AiFood.waiting_for_confirm, F.data == "cancel_aifood")
async def cancel_aifood_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("Добавление еды:", reply_markup=add_food_menu())
