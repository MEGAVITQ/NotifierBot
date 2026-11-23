from datetime import date
from html import escape

from aiogram_dialog import DialogManager

from bot.database import BotBD


def _format_date(value) -> str:
    try:
        return date.fromisoformat(str(value)).strftime("%d.%m.%Y")
    except ValueError:
        return str(value)


async def in_task_getter(dialog_manager: DialogManager, **middleware_data):
    task_id = dialog_manager.dialog_data.get("task_id")

    bd = BotBD()
    try:
        task = bd.get_task_by_id(task_id) if task_id is not None else None
    finally:
        bd.close_connection()

    if task is None:
        return {"data": "Задача не найдена", "date": "—", "status": 1}

    data, task_date, status = task
    return {
        "data": escape(str(data)),
        "date": _format_date(task_date),
        "status": status,
    }
