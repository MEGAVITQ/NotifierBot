from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode

from ..database import BotBD
from ..dialogs.States import MainStates

router = Router()


def _parse_task_id(data: str) -> int | None:
    _, _, raw_id = data.partition(":")
    try:
        return int(raw_id)
    except ValueError:
        return None


@router.callback_query(F.data.startswith("task_done:"))
async def task_done(callback: CallbackQuery) -> None:
    task_id = _parse_task_id(callback.data or "")

    bd = BotBD()
    try:
        status = bd.get_task_status(task_id) if task_id is not None else None
        if status is None:
            await callback.answer("Задача не найдена 🤷", show_alert=True)
            return
        already_done = status[0] == 1
        if not already_done:
            bd.change_status(task_id)
    finally:
        bd.close_connection()

    if already_done:
        await callback.answer("Задача уже выполнена ☑️")
    else:
        await callback.answer("Задача отмечена выполненной ✅")

    if callback.message is None or not callback.message.text:
        return

    text = callback.message.html_text
    if "✅ <b>Задача выполнена</b>" not in text:
        text = f"{text}\n\n✅ <b>Задача выполнена</b>"

    try:
        await callback.message.edit_text(text=text, reply_markup=None)
    except TelegramBadRequest:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass


@router.callback_query(F.data == "open_tasks")
async def open_tasks(
    callback: CallbackQuery,
    dialog_manager: DialogManager,
) -> None:
    user = callback.from_user

    bd = BotBD()
    try:
        if not bd.is_user_in_bd(user.id):
            bd.add_user(user.id, user.full_name)
    finally:
        bd.close_connection()

    await callback.answer()
    await dialog_manager.start(
        MainStates.main_menu,
        mode=StartMode.RESET_STACK,
        data={"user_id": user.id},
    )
