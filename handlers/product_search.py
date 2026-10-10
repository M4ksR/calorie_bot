from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from states import ProductSearch
from services.perek import search_perek
from services.openfoodfacts import search_openfoodfacts
from keyboards import add_food_menu

router = Router()

@router.callback_query(F.data == "find_food")
async def find_food_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.edit_text("Введите название продукта:")
    await state.set_state(ProductSearch.waiting_for_product)

def remove_duplicates(products):
    result = []
    seen = set()
    for food in products:
        name = (food.get('name') or "").strip().lower()
        brand = (food.get('brand').strip().lower() or "")
        key = (name, brand)
        if key in seen or not name: continue
        result.append(food)
        seen.add(key)
    return result

async def search_all_products(food_name):
    products = await search_perek(food_name, 20)
    if len(products) < 20:
        additional_products = await search_openfoodfacts(food_name, 20)
        products.extend(additional_products)
    return remove_duplicates(products)[:20]

@router.message(ProductSearch.waiting_for_product, F.text)
async def waiting_for_product_handler(message: Message, state: FSMContext) -> None:
    products = await search_all_products(message.text)
    if not products: await message.answer("Ничего не найдено", reply_markup=add_food_menu())
    await state.update_data(products=products, page=0)
