from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from states import ProductSearch
from services.perek import search_perek
from services.openfoodfacts import search_openfoodfacts
from keyboards import add_food_menu, products_search_menu, confirm_search_food, start_menu
from database import add_food_entry

router = Router()

def remove_duplicates(products):
    result = []
    seen = set()
    for food in products:
        name = (food.get('name') or "").strip().lower()
        brand = (food.get('brand') or "").strip().lower()
        key = (name, brand)
        if key in seen or not name: continue
        result.append(food)
        seen.add(key)
    return result

async def search_all_products(food_name):
    products = await search_perek(food_name, 5)
    if len(products) < 5:
        additional_products = await search_openfoodfacts(food_name, 10)
        products.extend(additional_products)
    return remove_duplicates(products)[:5]

@router.callback_query(F.data == "find_food")
async def find_food_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.edit_text("Введите название продукта:")
    await state.set_state(ProductSearch.waiting_for_product)

@router.message(ProductSearch.waiting_for_product, F.text)
async def waiting_for_product_handler(message: Message, state: FSMContext) -> None:
    products = await search_all_products(message.text)
    if not products:
        await state.clear()
        await message.answer("Ничего не найдено", reply_markup=add_food_menu())
    else:
        await state.update_data(products=products)
        await message.answer("Найденные совпадения:", reply_markup=products_search_menu(products))

@router.callback_query(ProductSearch.waiting_for_product, F.data.startswith("product_select_"))
async def selected_product_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    index = int(callback.data.split('_')[-1])
    data = await state.get_data()
    products = data.get("products", [])
    await state.update_data(selected_product=products[index])
    await state.set_state(ProductSearch.waiting_for_weight)
    await callback.message.edit_text("Введите вес:")

@router.message(ProductSearch.waiting_for_weight, F.text)
async def waiting_for_weight_handler(message: Message, state: FSMContext) -> None:
    try:
        weight = float(message.text.replace(',','.'))
    except ValueError:
        await message.answer("Неверный формат ввода")
        return

    if weight <= 0:
        await message.answer("Неверный формат ввода")
        return

    data = await state.get_data()
    product = data.get('selected_product', {})
    coef = weight / 100

    name = product.get('name', "")
    calories = (product.get('calories') or 0) * coef
    protein = (product.get('protein', 0) or 0) * coef
    fat = (product.get('fat', 0) or 0) * coef
    carbs = (product.get('carbs', 0) or 0) * coef

    await state.update_data(name=name,
                            weight=weight,
                            calories=calories,
                            protein=protein,
                            fat=fat,
                            carbs=carbs)

    await state.set_state(ProductSearch.waiting_for_confirm)
    await message.answer(f"{name}, {weight}г\n\n"
                         f"{calories}ккал\n"
                         f"Б: {protein:.1f}\n"
                         f"Ж: {fat:.1f}\n"
                         f"У: {carbs:.1f}",
                         reply_markup=confirm_search_food())

@router.callback_query(ProductSearch.waiting_for_confirm, F.data == "confirm_search_food")
async def confirm_search_food_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    await add_food_entry(callback.from_user.id,
                         data['name'],
                         data['weight'],
                         data['calories'],
                         data['protein'],
                         data['fat'],
                         data['carbs'])
    await state.clear()
    await callback.message.edit_text("Блюдо добавлено\n\n"
                                     "Calorie counter", reply_markup=start_menu())

@router.callback_query(ProductSearch.waiting_for_confirm, F.data == "cancel_search_food")
async def cancel_search_product_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("Добавление еды:", reply_markup=add_food_menu())
