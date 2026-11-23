from datetime import date
from html import escape

from aiogram_dialog import DialogManager

from bot.database import BotBD


def _format_date(value) -> str:
    try:
        return date.fromisoformat(str(value)).strftime("%d.%m.%Y")
    except ValueError:
        return str(value)


async def main_getter(dialog_manager: DialogManager, **middleware_data):
    user_id = dialog_manager.start_data.get("user_id")

    bd = BotBD()
    try:
        rows = bd.get_user_notifications(user_id)
    finally:
        bd.close_connection()

    # Сначала активные, внутри группы — ближайшие по дедлайну.
    rows = sorted(rows, key=lambda row: (row[3], str(row[2])))

    tasks = [
        {
            "id": task_id,
            "data": escape(str(text)),
            "date": _format_date(task_date),
            "status": status,
        }
        for task_id, text, task_date, status in rows
    ]

    return {
        "tasks": tasks,
        "has_tasks": bool(tasks),
        "tasks_count": len(tasks),
    }
