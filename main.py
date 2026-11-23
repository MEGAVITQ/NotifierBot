import asyncio
import logging
from contextlib import suppress

from aiogram import Bot
from aiogram_dialog import setup_dialogs

from bot.database import BotBD
from bot.dialogs import main_dialog
from bot.main import dp, bot
from bot.routers import routers
from bot.services import reminder_worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

reminder_task: asyncio.Task | None = None


async def on_startup(bot: Bot) -> None:
    global reminder_task

    bd = BotBD()
    try:
        bd.create_tables()
    finally:
        bd.close_connection()

    reminder_task = asyncio.create_task(reminder_worker(bot))
    print("bot is polling")


async def on_shutdown(bot: Bot) -> None:
    global reminder_task

    if reminder_task is not None:
        reminder_task.cancel()
        with suppress(asyncio.CancelledError):
            await reminder_task
        reminder_task = None


async def main() -> None:
    dp.include_router(routers)
    dp.include_router(main_dialog())
    setup_dialogs(dp)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


def start_bot():
    asyncio.run(main())
