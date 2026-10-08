from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from states import DailyAllowance
from keyboards import calculation_of_daily_allowance, purpose, activity, start_menu, gender

from database import get_daily_calories, set_daily_calories

router = Router()

@router.callback_query(F.data == "Find_out_daily")
async def Find_Out_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    daily_calories = await get_daily_calories(callback.from_user.id)
    if daily_calories is None: await callback.message.edit_text("Сначала рассчитайте свою норму",
                                                                reply_markup=calculation_of_daily_allowance())
    else: await callback.message.edit_text(f"Ваша норма: {daily_calories}")

@router.callback_query(F.data == "Calculate_daily")
async def Calculate_daily_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(DailyAllowance.waiting_for_gender)
    await callback.message.edit_text("Выберите ваш пол", reply_markup=gender())

@router.callback_query(DailyAllowance.waiting_for_gender, F.data)
async def DailyAllowance_gender_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(gender=callback.data)
    await state.set_state(DailyAllowance.waiting_for_weight)
    await callback.message.edit_text("Введите ваш вес")

@router.message(DailyAllowance.waiting_for_weight, F.text)
async def DailyAllowance_weight_handler(message: Message, state: FSMContext) -> None:
    try:
        value = float(message.text.strip())
    except ValueError:
        await message.answer("Неверный формат")
        return

    if value <= 0:
        await message.answer("Неверный формат")
        return

    await state.update_data(weight=value)
    await state.set_state(DailyAllowance.waiting_for_height)
    await message.answer("Введите ваш рост")

@router.message(DailyAllowance.waiting_for_height, F.text)
async def DailyAllowance_height_handler(message: Message, state: FSMContext) -> None:
    try:
        value = float(message.text.strip())
    except ValueError:
        await message.answer("Неверный формат")
        return

    if value <= 0:
        await message.answer("Неверный формат")
        return

    await state.update_data(height=value)
    await state.set_state(DailyAllowance.waiting_for_age)
    await message.answer("Введите ваш возраст")

@router.message(DailyAllowance.waiting_for_age, F.text)
async def DailyAllowance_age_handler(message: Message, state: FSMContext) -> None:
    try:
        value = int(message.text.strip())
    except ValueError:
        await message.answer("Неверный формат")
        return

    if value <= 0:
        await message.answer("Неверный формат")
        return

    await state.update_data(age=value)
    await state.set_state(DailyAllowance.waiting_for_activity)
    await message.answer("Оцените вашу активность", reply_markup=activity())

@router.callback_query(DailyAllowance.waiting_for_activity, F.data)
async def DailyAllowance_activity_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    if callback.data == "Sit": coef = 1.2
    elif callback.data == "Lite": coef = 1.42
    elif callback.data == "Medium": coef = 1.55
    elif callback.data == "Hard": coef = 1.8
    else: await callback.answer("Неверный формат") ; return

    await state.update_data(activity=coef)
    await state.set_state(DailyAllowance.waiting_for_purpose)
    await callback.message.edit_text("Выберите вашу цель", reply_markup=purpose())

@router.callback_query(DailyAllowance.waiting_for_purpose, F.data)
async def DailyAllowance_purpose_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    if callback.data == "WeightLoss": coef = -15
    elif callback.data == "WeightMaintenance": coef = 0
    elif callback.data == "WeightGain": coef = 12
    else: await callback.answer("Неверный формат") ; return

    data = await state.get_data()
    scale = (10 * data['weight']) + (6.25 * data['height']) - (5 * data['age'])

    if data['gender'] == "Male": scale += 5
    else: scale -= 161

    scale *= data['activity']
    scale *= (100 + coef) / 100

    await callback.message.edit_text(f"Ваша дневная норма: {scale}", reply_markup=start_menu())
    await set_daily_calories(callback.from_user.id, scale)
    await state.clear()

@router.callback_query(F.data == "Back_daily")
async def Back_daily_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text("Calorie counter", reply_markup=start_menu())
