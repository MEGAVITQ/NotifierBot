from aiogram_dialog import Dialog

from .windows import in_task_window, main_window


def main_dialog() -> Dialog:
    return Dialog(main_window(), in_task_window())
