from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot.database import BotBD


async def on_complete_clicked(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    *args,
) -> None:
    task_id = dialog_manager.dialog_data.get("task_id")

    bd = BotBD()
    try:
        status = bd.get_task_status(task_id) if task_id is not None else None
        if status is None:
            await callback.answer("Задача не найдена 🤷", show_alert=True)
            return

        if status[0] == 1:
            await callback.answer("Задача уже выполнена ☑️")
            return

        bd.change_status(task_id)
    finally:
        bd.close_connection()

    dialog_manager.dialog_data.pop("task_id", None)
    await callback.answer("Задача отмечена выполненной ✅")
    await dialog_manager.back()
