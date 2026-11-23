from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button



async def on_back_clicked(callback: CallbackQuery, button: Button,
                     dialog_manager: DialogManager, *args) -> None:
    dialog_manager.dialog_data.clear()
    await dialog_manager.back()