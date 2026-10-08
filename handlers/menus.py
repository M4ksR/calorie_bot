from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards import calculation_of_daily_allowance, add_food_menu, start_menu
from database import get_daily_calories, get_today_calories

router = Router()

@router.callback_query(F.data == "DailyAllowance")
async def DailyAllowance_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text("Расчет дневной нормы калорий", reply_markup=calculation_of_daily_allowance())

@router.callback_query(F.data == "AddFood")
async def AddFood_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text("Добавление еды:", reply_markup=add_food_menu())

@router.callback_query(F.data == "LeftCalories")
async def LeftCalories_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()

    # Получаем дневную норму
    # Если нормы еще нет, то говорим пользователю,
    # что ее нужно рассчитать
    daily = await get_daily_calories(callback.from_user.id)
    if daily is None:
        await callback.message.edit_text("Сначала рассчитайте свою норму",
                                                                reply_markup=calculation_of_daily_allowance())
        return

    # Получаем съеденные калории за сегодня
    # Это значение >= 0
    eaten = await get_today_calories(callback.from_user.id)

    await callback.message.edit_text(f"На сегодня осталось: {daily - eaten}")

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
