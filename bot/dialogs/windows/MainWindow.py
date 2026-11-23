from aiogram_dialog import Window
from aiogram_dialog.widgets.markup.force_reply import ForceReplyFactory
from aiogram_dialog.widgets.text import Format, Const, Progress, List
from aiogram_dialog.widgets.kbd import Row, ScrollingGroup, Button, Group, ListGroup, PrevPage, NextPage, Select
import operator
from ..Callbacks.OnTaskClicked import on_task_clicked
from ..getters.MainGetter import main_getter
from bot.dialogs.States import MainStates


def main_window():
    window = Window(
        Format("""<b>---ВАШИ ЗАДАЧИ---</b>\n"""),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),  # Предположим, item[0] - это текст задачи
                id="task_select",
                item_id_getter=operator.itemgetter(0),  # ID задачи (например, индекс или ключ)
                items="tasks",
                on_click=on_task_clicked,  # Ваша функция-обработчик
            ),
            id="tasks_scroll",
            width=1,  # 1 кнопка в ряд
            height=5,  # 5 кнопок на странице
        ),
        state=MainStates.main_menu,
        getter=main_getter
    )
    return window