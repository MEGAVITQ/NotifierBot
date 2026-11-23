from datetime import datetime
from html import escape

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, StartMode

from ..States.AddNotifyStates import AddNotifyStates
from ..database import BotBD
from ..dialogs.States import MainStates

router = Router()

DIVIDER = "━━━━━━━━━━━━━━━━━━"


def _ensure_user(bd: BotBD, user: types.User) -> None:
    if not bd.is_user_in_bd(user.id):
        bd.add_user(user.id, user.full_name)


async def _show_tasks(message: types.Message, dialog_manager: DialogManager) -> None:
    bd = BotBD()
    try:
        _ensure_user(bd, message.from_user)
    finally:
        bd.close_connection()

    await dialog_manager.start(
        MainStates.main_menu,
        mode=StartMode.RESET_STACK,
        data={"user_id": message.from_user.id},
    )


@router.message(F.text == "➕ Добавить задачу")
async def add_notify(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AddNotifyStates.ASK_DATA)
    await message.answer(
        "📝 <b>Шаг 1 из 2.</b> Опишите задачу:\n\n"
        "<i>Например: «Позвонить в банк»</i>"
    )


@router.message(AddNotifyStates.ASK_DATA, F.text)
async def ask_data(
    message: types.Message,
    state: FSMContext,
    dialog_manager: DialogManager,
) -> None:
    if message.text == "📋 Мои задачи":
        await state.clear()
        await _show_tasks(message, dialog_manager)
        return

    await state.update_data(task_text=message.text)
    await state.set_state(AddNotifyStates.ASK_DATE)
    await message.answer(
        "📅 <b>Шаг 2 из 2.</b> Введите дедлайн в формате "
        "<code>ГГГГ-ММ-ДД</code>:\n\n"
        "<i>Например: 2026-12-31</i>"
    )


@router.message(AddNotifyStates.ASK_DATE, F.text)
async def ask_date(
    message: types.Message,
    state: FSMContext,
    dialog_manager: DialogManager,
) -> None:
    if message.text == "📋 Мои задачи":
        await state.clear()
        await _show_tasks(message, dialog_manager)
        return

    raw_date = (message.text or "").strip()
    try:
        deadline = datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(
            "⚠️ Не получилось разобрать дату.\n\n"
            "Введите её в формате <code>ГГГГ-ММ-ДД</code>, "
            "например <code>2026-12-31</code>."
        )
        return

    data = (await state.get_data()).get("task_text", "")

    bd = BotBD()
    try:
        _ensure_user(bd, message.from_user)
        bd.add_notification(message.from_user.id, data, deadline)
    finally:
        bd.close_connection()

    await state.clear()
    await message.answer(
        "✅ <b>Задача добавлена!</b>\n"
        f"{DIVIDER}\n\n"
        f"📝 {escape(data or '')}\n"
        f"📅 Дедлайн: <b>{deadline.strftime('%d.%m.%Y')}</b>\n\n"
        "🔔 Напомню в <b>08:00</b> за 3 дня, за 1 день "
        "и в день дедлайна."
    )
    await dialog_manager.start(
        MainStates.main_menu,
        mode=StartMode.RESET_STACK,
        data={"user_id": message.from_user.id},
    )


@router.message(F.text == "📋 Мои задачи")
async def my_tasks(message: types.Message, dialog_manager: DialogManager) -> None:
    await _show_tasks(message, dialog_manager)
