from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button



async def on_task_clicked(callback: CallbackQuery, button: Button,
                     dialog_manager: DialogManager, *args) -> None:
    print(callback.data, button.widget_id)