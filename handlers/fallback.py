from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message()
async def another_type_of_message(message: Message) -> None:
    await message.answer(f"Сообщение не распознано, используйте /help")
