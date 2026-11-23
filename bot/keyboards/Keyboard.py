from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton

def get_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="Добавить задачу"),
        KeyboardButton(text="Вывести задачи")
    ]], resize_keyboard=True)

    return keyboard