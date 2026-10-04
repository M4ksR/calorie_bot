from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def message_handler(message: Message) -> None:
    await message.answer(f"User wrote: {message.text}")

@router.message()
async def another_type_of_message(message: Message) -> None:
    await message.answer("The message you sent in this chat is not a familiar command or text, use /help")
