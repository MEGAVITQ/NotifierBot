import asyncio

from bot.dialogs import main_dialog
from bot.database import BotBD
from bot.main import dp, bot
from bot.routers import routers
from aiogram_dialog import setup_dialogs


async def on_startup():
    bd = BotBD()
    bd.create_tables()
    print("bot is polling")



async def on_shutdown():
    pass

async def main() -> None:
    dp.include_router(routers)
    dp.include_router(main_dialog())
    setup_dialogs(dp)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


def start_bot():
    asyncio.run(main())
