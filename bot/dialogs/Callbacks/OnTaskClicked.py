from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button


async def on_task_clicked(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    item_id,
    *args,
) -> None:
    try:
        task_id = int(item_id)
    except (TypeError, ValueError):
        task_id = item_id

    dialog_manager.dialog_data["task_id"] = task_id
    await dialog_manager.next()
