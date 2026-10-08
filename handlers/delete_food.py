from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import delete_food_entry, get_today_food_entries

router = Router()

def delete_food_menu(data):
    builder = InlineKeyboardBuilder()
    for i in data:
        builder.button(text=f"{i[1]} - {i[2]}г - {i[3]:.0f}ккал", callback_data=f"delete_food_{i[0]}")

    builder.button(text="Назад", callback_data="back")
    builder.adjust(1)

    return builder.as_markup()

@router.callback_query(F.data == "DeleteFood")
async def delete_food_callback_handler(callback: CallbackQuery):
    await callback.answer()
    data = await get_today_food_entries(callback.from_user.id)
    text = "Сегодня у вас нет добавленных блюд" if not data else "Выберите, что хотите удалить"
    await callback.message.edit_text(text, reply_markup=delete_food_menu(data))

@router.callback_query(F.data.startswith("delete_food_"))
async def delete_meal_handler(callback: CallbackQuery):
    await delete_food_entry(int(callback.data.split('_')[-1]), callback.from_user.id)
    data = await get_today_food_entries(callback.from_user.id)
    await callback.answer("Запись удалена")
    await callback.message.edit_text("Выберите, что хотите удалить", reply_markup=delete_food_menu(data))
