from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Case, Const, Format

from ..Callbacks import on_back_clicked, on_complete_clicked, on_delete_clicked
from ..getters import in_task_getter
from ..States import MainStates

DIVIDER = "━━━━━━━━━━━━━━━━━━"


def in_task_window():
    window = Window(
        Format(
            f"📝 <b>Задача</b>\n{DIVIDER}\n\n"
            "{data}\n\n"
            "📅 Дедлайн: <b>{date}</b>\n"
        ),
        Case(
            {
                0: Const("🟢 Статус: активная"),
                1: Const("✅ Статус: выполнена"),
            },
            selector="status",
        ),
        Button(
            Const("⬅️ Назад"),
            on_click=on_back_clicked,
            id="back",
        ),
        Button(
            Case(
                {
                    0: Const("✅ Выполнить"),
                    1: Const("☑️ Уже выполнено"),
                },
                selector="status",
            ),
            on_click=on_complete_clicked,
            id="complete",
        ),
        Button(
            Const("Удалить"),
            on_click=on_delete_clicked,
            id="delete",
        ),
        getter=in_task_getter,
        state=MainStates.InTask,
    )
    return window
