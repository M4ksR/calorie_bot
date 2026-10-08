import asyncio
import logging
import sys

from database import init_database
from aiogram import Bot, Dispatcher

from config import TOKEN

from handlers.commands import router as commands_router
from handlers.custom_food import router as custom_food_router
from handlers.delete_food import router as delete_food_router
from handlers.daily_allowance import router as daily_allowance_router
from handlers.menus import router as menus_router
from handlers.fallback import router as fallback_router

async def main() -> None:
    bot = Bot(token=TOKEN)

    dp = Dispatcher()
    dp.include_router(commands_router)
    dp.include_router(custom_food_router)
    dp.include_router(delete_food_router)
    dp.include_router(daily_allowance_router)
    dp.include_router(menus_router)
    dp.include_router(fallback_router)

    await init_database()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
