from aiogram import Router, F
from aiogram.types import CallbackQuery

from aiogram.fsm.context import FSMContext
from keyboards import add_food_menu, start_menu

router = Router()

@router.callback_query(F.data == "DailyAllowance")
async def DailyAllowance_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("Your daily allowance is: {value}")

@router.callback_query(F.data == "AddFood")
async def AddFood_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text("Добавление еды:", reply_markup=add_food_menu())

@router.callback_query(F.data == "LeftCalories")
async def LeftCalories_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("Today you have {value} calories")

@router.callback_query(F.data == "DeleteFood")
async def DeleteFood_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("This function is under development")

@router.callback_query(F.data == "save_food")
async def save_food_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("This function is under development")

@router.callback_query(F.data == "find_food")
async def find_food_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("This function is under development")

@router.callback_query(F.data == "back")
async def back_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text("Calorie Counter", reply_markup=start_menu())

@router.callback_query(F.data == "confirm_food")
async def confirm_food_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    await callback.message.answer(f"Блюдо {data['food_name']} добавлено")
    await state.clear()

@router.callback_query(F.data == "cancel_food")
async def confirm_food_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.answer("Добавление отменено", reply_markup=add_food_menu())
