from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup


def get_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="➕ Добавить задачу"),
            KeyboardButton(text="📋 Мои задачи"),
        ]],
        resize_keyboard=True,
    )
    return keyboard
