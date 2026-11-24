from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot.States.AddNotifyStates import AddNotifyStates


async def on_add_task_clicked(callback: CallbackQuery,button: Button,
                              dialog_manager: DialogManager,*args) -> None:

    state: FSMContext = dialog_manager.middleware_data["state"]

    await state.set_state(AddNotifyStates.ASK_DATA)
    await callback.answer()
    await callback.message.answer(
        "📝 <b>Шаг 1 из 2.</b> Опишите задачу:\n\n"
        "<i>Например: «Позвонить в банк»</i>"
    )
