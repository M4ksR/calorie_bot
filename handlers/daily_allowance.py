from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from states import DailyAllowance

from keyboards import (calculation_of_daily_allowance,
                       purpose,
                       activity,
                       start_menu,
                       gender,
                       go_to_start_menu,
                       cancel_daily_allowance)

from database import get_daily_calories, set_daily_calories

router = Router()

@router.callback_query(F.data == "DailyAllowance")
async def DailyAllowance_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text("Расчет дневной нормы калорий", reply_markup=calculation_of_daily_allowance())

@router.callback_query(F.data == "Find_out_daily")
async def Find_Out_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    daily_calories = await get_daily_calories(callback.from_user.id)
    if not daily_calories: await callback.message.edit_text("Сначала рассчитайте свою норму",
                                                                reply_markup=calculation_of_daily_allowance())
    else: await callback.message.edit_text("Ваша норма:\n\n"
                                           f"К:  {daily_calories[0]:.1f} ккал\n"
                                           f"Б:  {daily_calories[1]:.1f} г\n"
                                           f"Ж:  {daily_calories[2]:.1f} г\n"
                                           f"У:  {daily_calories[3]:.1f} г",
                                           reply_markup=go_to_start_menu())

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
    await callback.message.edit_text("Введите ваш вес", reply_markup=cancel_daily_allowance())

@router.message(DailyAllowance.waiting_for_weight, F.text)
async def DailyAllowance_weight_handler(message: Message, state: FSMContext) -> None:
    try:
        value = float(message.text.strip())
    except ValueError:
        await message.answer("Неверный формат", reply_markup=go_to_start_menu())
        return

    if value <= 0:
        await message.answer("Неверный формат", reply_markup=go_to_start_menu())
        return

    await state.update_data(weight=value)
    await state.set_state(DailyAllowance.waiting_for_height)
    await message.answer("Введите ваш рост", reply_markup=cancel_daily_allowance())

@router.message(DailyAllowance.waiting_for_height, F.text)
async def DailyAllowance_height_handler(message: Message, state: FSMContext) -> None:
    try:
        value = float(message.text.strip())
    except ValueError:
        await message.answer("Неверный формат", reply_markup=go_to_start_menu())
        return

    if value <= 0:
        await message.answer("Неверный формат", reply_markup=go_to_start_menu())
        return

    await state.update_data(height=value)
    await state.set_state(DailyAllowance.waiting_for_age)
    await message.answer("Введите ваш возраст", reply_markup=cancel_daily_allowance())

@router.message(DailyAllowance.waiting_for_age, F.text)
async def DailyAllowance_age_handler(message: Message, state: FSMContext) -> None:
    try:
        value = int(message.text.strip())
    except ValueError:
        await message.answer("Неверный формат", reply_markup=go_to_start_menu())
        return

    if value <= 0:
        await message.answer("Неверный формат", reply_markup=go_to_start_menu())
        return

    await state.update_data(age=value)
    await state.set_state(DailyAllowance.waiting_for_activity)
    await message.answer("Оцените вашу активность", reply_markup=activity())

@router.callback_query(DailyAllowance.waiting_for_activity, F.data)
async def DailyAllowance_activity_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    if callback.data == "Sit": coef = 1.2
    elif callback.data == "Lite": coef = 1.375
    elif callback.data == "Medium": coef = 1.55
    elif callback.data == "Hard": coef = 1.725
    else: await callback.answer("Неверный формат", reply_markup=go_to_start_menu()) ; return

    await state.update_data(activity=coef)
    await state.set_state(DailyAllowance.waiting_for_purpose)
    await callback.message.edit_text("Выберите вашу цель", reply_markup=purpose())

@router.callback_query(DailyAllowance.waiting_for_purpose, F.data)
async def DailyAllowance_purpose_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    if callback.data == "WeightLoss":
        coef = (-15, 30, 30, 40)
    elif callback.data == "WeightMaintenance":
        coef = (0, 25, 30, 45)
    elif callback.data == "WeightGain":
        coef = (12, 25, 25, 50)
    else:
        await callback.answer("Неверный формат", reply_markup=go_to_start_menu())
        return

    data = await state.get_data()
    scale = (10 * data['weight']) + (6.25 * data['height']) - (5 * data['age'])

    if data['gender'] == "Male": scale += 5
    else: scale -= 161

    scale *= data['activity']
    scale *= (100 + coef[0]) / 100

    protein = scale * coef[1] / (100 * 4)
    fat = scale * coef[2] / (100 * 9)
    carbs = scale * coef[3] / (100 * 4)

    await callback.message.edit_text("Ваша дневная норма:\n\n"
                                     f"К:  {scale:.1f} ккал\n"
                                     f"Б:  {protein:.1f} г\n"
                                     f"Ж:  {fat:.1f} г\n"
                                     f"У:  {carbs:.1f}",
                                     reply_markup=start_menu())

    await set_daily_calories(callback.from_user.id, scale, protein, fat, carbs)
    await state.clear()

@router.callback_query(F.data == "Back_daily")
async def Back_daily_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text("Calorie counter", reply_markup=start_menu())
