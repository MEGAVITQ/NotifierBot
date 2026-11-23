from aiogram import Router
from aiogram import types, F
from aiogram.types import CallbackQuery
from aiogram.filters import Command

from ..database import BotBD

from aiogram_dialog import DialogManager
from aiogram_dialog import StartMode
from aiogram_dialog.widgets.kbd import Button

from datetime import datetime as dt

from ..dialogs.States import MainStates
from ..keyboards.Keyboard import get_keyboard

router = Router()

@router.message(F.text == "/start")
async def start(message: types.Message, dialog_manager: DialogManager) -> None:
    await message.answer("Здраствуйте, я ваш бот-помощник, я буду напоминать о ваших делах", reply_markup=get_keyboard())
    bd = BotBD()
    user_id = message.from_user.id
    if not bd.is_user_in_bd(user_id=user_id):
        bd.add_user(user_id, message.from_user.full_name)
    await dialog_manager.start(MainStates.main_menu, mode=StartMode.RESET_STACK, data={"user_id": message.from_user.id})
    bd.close_connection()

@router.message(F.text.split()[0] == "/add_notify")
async def add_notify(message: types.Message) -> None:
    bd = BotBD()
    message_split = message.text.split(" ")
    data = message_split[1]
    date = dt.fromisoformat(message_split[2]).date()
    user_id = message.from_user.id
    print(user_id, data, date)
    bd.add_notification(user_id, data, date)
    bd.close_connection()

@router.message(F.text.split()[0] == "/get_notifications")
async def get_notify(message: types.Message) -> None:
    bd = BotBD()
    notis = bd.get_user_notifications(message.from_user.id)
    print(notis)
    bd.close_connection()