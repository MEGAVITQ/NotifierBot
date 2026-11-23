from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from datetime import datetime

from aiogram_dialog import DialogManager, StartMode

from States.AddNotifyStates import AddNotifyStates
from dialogs.States import MainStates
from ..database import BotBD
router = Router()

@router.message(F.text == "Добавить задачу")
async def add_notify(message: types.Message, state: FSMContext):
    await message.answer("<b>Опишите задачу.</b>")
    await state.set_state(AddNotifyStates.ASK_DATA)

@router.message(AddNotifyStates.ASK_DATA)
async def ask_data(message: types.Message, state: FSMContext):
    await state.set_data({"data" : message.text})
    await message.answer("<b>Введите дату, до которой нужно сделать задачу.</b>")
    await state.set_state(AddNotifyStates.ASK_DATE)

@router.message(AddNotifyStates.ASK_DATE)
async def ask_date(message: types.Message, state: FSMContext, dialog_manager: DialogManager):
    data = (await state.get_data()).get("data")
    date = datetime.strptime(message.text.strip(), "%Y-%m-%d").date()
    bd = BotBD()
    bd.add_notification(message.from_user.id, data, date)
    bd.close_connection()
    await message.answer("<b>Задача добавлена.</b>")
    await state.clear()
    await dialog_manager.start(MainStates.main_menu, mode=StartMode.RESET_STACK, data={"user_id": message.from_user.id})