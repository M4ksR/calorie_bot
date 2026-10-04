from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from keyboards import start_menu

router = Router()

@router.message(CommandStart()) #/start
async def command_start_handler(message: Message) -> None:
    await message.answer("Calorie Counter", reply_markup=start_menu())

@router.message(Command("help"))
async def command_help(message : Message) -> None:
    await message.answer("User used /help")

@router.message(Command("about"))
async def command_about(message : Message) -> None:
    await message.answer("User used /about")

@router.message(F.text.startswith("/"))
async def unknown_command(message : Message) -> None:
    await message.answer("Unknown command, use /help")
