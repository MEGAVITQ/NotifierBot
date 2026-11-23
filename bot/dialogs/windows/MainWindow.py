import operator

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Case, Const, Format
from magic_filter import F

from ..Callbacks import on_add_task_clicked, on_task_clicked
from ..getters.MainGetter import main_getter
from ..States import MainStates

DIVIDER = "━━━━━━━━━━━━━━━━━━"


def main_window():
    window = Window(
        Format(f"🕒 <b>Ваши задачи</b>  ·  {{tasks_count}}\n{DIVIDER}\n"),
        Case(
            {
                True: Format("Выберите задачу, чтобы открыть её 👇"),
                False: Format(
                    "✨ Пока задач нет.\n"
                    "Нажмите «➕ Добавить задачу» внизу."
                ),
            },
            selector="has_tasks",
        ),
        ScrollingGroup(
            Select(
                Case(
                    {
                        0: Format("🟢 {item[date]} — {item[data]}"),
                        1: Format("✅ {item[date]} — {item[data]}"),
                    },
                    selector=F["item"]["status"],
                ),
                id="task_select",
                item_id_getter=operator.itemgetter("id"),
                items="tasks",
                on_click=on_task_clicked,
            ),
            id="tasks_scroll",
            width=1,
            height=5,
            hide_on_single_page=True,
        ),
        Button(
            Const("➕ Добавить задачу"),
            id="add_task",
            on_click=on_add_task_clicked,
        ),
        state=MainStates.main_menu,
        getter=main_getter,
    )
    return window
