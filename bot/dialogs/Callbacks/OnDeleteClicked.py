from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager

from bot.database import BotBD

async def on_delete_clicked(callback: CallbackQuery,button: Button,
                          dialog_manager: DialogManager,*args,) -> None:

    bd = BotBD()
    task_id = dialog_manager.dialog_data.get("task_id")
    bd.delete_task(task_id)
    bd.close_connection()
    dialog_manager.dialog_data.clear()
    await callback.answer("Задача удалена")
    await dialog_manager.back()