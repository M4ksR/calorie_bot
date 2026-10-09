from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states import SavedFood
from keyboards import saved_food_menu, add_food_menu, start_menu
from database import add_food_entry, get_saved_food_by_id, get_saved_food

router = Router()

@router.callback_query(F.data == "save_food")
async def save_food_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    data = await get_saved_food(callback.from_user.id)
    if not data:
        await callback.message.edit_text("У вас пока нет сохраненных блюд", reply_markup=add_food_menu())
        return
    await callback.message.edit_text("Выберите сохраненное блюдо", reply_markup=saved_food_menu(data))

@router.callback_query(SavedFood.waiting_for_confirm, F.data == "saved_food_confirm")
async def saved_food_confirm_handler(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    coef = data['weight'] / 100
    await add_food_entry(callback.from_user.id,
                         data['food_name'],
                         data['weight'],
                         data['calories'] * coef,
                         data['protein'] * coef,
                         data['fat'] * coef,
                         data['carbs'] * coef)
    await callback.message.edit_text("Блюдо успешно добавлено", reply_markup=start_menu())
    await state.clear()

@router.callback_query(SavedFood.waiting_for_confirm, F.data == "saved_food_cancel")
async def saved_food_cancel_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("Добавление отменено\n\n"
                                     "Calorie counter",
                                     reply_markup=start_menu())

@router.callback_query(F.data.startswith("saved_food_"))
async def saved_food_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    data = await get_saved_food_by_id(int(callback.data.split('_')[-1]), callback.from_user.id)
    await state.update_data(food_name=data[0],
                            calories=data[1],
                            protein=data[2],
                            fat=data[3],
                            carbs=data[4])

    await state.set_state(SavedFood.waiting_for_weight)
    await callback.message.edit_text("Введите вес блюда")

@router.message(SavedFood.waiting_for_weight, F.text)
async def saved_food_weight_handler(message: Message, state: FSMContext) -> None:
    try:
        weight = float(message.text)
    except ValueError:
        await message.answer("Неверный формат")
        return

    if weight < 0:
        await message.answer("Неверный формат")
        return

    await state.update_data(weight=weight)
    await state.set_state(SavedFood.waiting_for_confirm)

    builder = InlineKeyboardBuilder()

    builder.button(text="Подтвердить", callback_data="saved_food_confirm")
    builder.button(text="Отменить", callback_data="saved_food_cancel")
    builder.adjust(1)

    await message.answer("Подтвердить добавление", reply_markup=builder.as_markup())
