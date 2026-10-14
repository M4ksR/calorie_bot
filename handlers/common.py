from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards import start_menu

router = Router()

@router.callback_query(F.data == "go_to_start_menu")
async def go_to_start_menu_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Calorie counter", reply_markup=start_menu())
