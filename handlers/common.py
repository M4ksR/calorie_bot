from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards import start_menu, calculation_of_daily_allowance, add_food_menu

router = Router()

@router.callback_query(F.data == "go_to_start_menu")
async def go_to_start_menu_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text("Calorie counter", reply_markup=start_menu())

@router.callback_query(F.data == "cancel_daily_allowance")
async def back_daily_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("Расчет дневной нормы калорий", reply_markup=calculation_of_daily_allowance())

@router.callback_query(F.data == "cancel_add_food")
async def back_add_food_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("Добавление еды:", reply_markup=add_food_menu())
