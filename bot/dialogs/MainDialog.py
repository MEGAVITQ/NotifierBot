from .windows.MainWindow import main_window
from aiogram_dialog import Dialog
from aiogram import Router

def main_dialog() -> Dialog:
    dialog = Dialog(main_window())
    return dialog