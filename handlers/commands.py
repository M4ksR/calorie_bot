from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from keyboards import start_menu, go_to_start_menu

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Calorie Counter", reply_markup=start_menu())

@router.message(Command("help"))
async def command_help(message : Message) -> None:
    await message.answer("Описание бота можно почитать <a href='https://github.com/M4ksR/calorie_bot#'>здесь</a>",
                         parse_mode="HTML",
                         disable_web_page_preview=True,
                         reply_markup=go_to_start_menu())

@router.message(F.text.startswith("/"))
async def unknown_command(message : Message) -> None:
    await message.answer("Данная команда не является стандартной, используйте /help")
