from datetime import datetime
from html import escape

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, StartMode

from ..database import BotBD
from ..dialogs.States import MainStates
from ..keyboards.Keyboard import get_keyboard

router = Router()

DIVIDER = "━━━━━━━━━━━━━━━━━━"


def _ensure_user(bd: BotBD, user: types.User) -> None:
    if not bd.is_user_in_bd(user.id):
        bd.add_user(user.id, user.full_name)


@router.message(Command("help"))
async def start(message: types.Message) -> None:
    await message.answer("1. /start -- приветствие от бота и запуск диалога\n"
                         "2. /tasks -- запуск диалога\n"
                         "3. /add_notify [текст задачи] [дата]-- добавляет в бд новую задачу\n"
                         "4. /get_notifications -- выводит список задач(без запуска\\рестарта диалога)"
                         "5. /help -- вызов этого сообщения")



@router.message(Command("start"))
async def start(
    message: types.Message,
    dialog_manager: DialogManager,
    state: FSMContext,
) -> None:
    name = escape(message.from_user.first_name or "друг")

    await state.clear()

    bd = BotBD()
    try:
        _ensure_user(bd, message.from_user)
    finally:
        bd.close_connection()

    await message.answer(
        f"👋 <b>Привет, {name}!</b>\n"
        f"{DIVIDER}\n\n"
        "Я помогу не забыть о важных делах.\n\n"
        "🔔 Напоминания приходят в <b>08:00</b> по Москве:\n"
        "• за <b>3 дня</b> до дедлайна\n"
        "• за <b>1 день</b>\n"
        "• в <b>день дедлайна</b>\n"
        "⚠️ и отдельно — если задача просрочена.\n\n"
        "👇 Ваши задачи:",
        reply_markup=get_keyboard(),
    )
    await dialog_manager.start(
        MainStates.main_menu,
        mode=StartMode.RESET_STACK,
        data={"user_id": message.from_user.id},
    )


@router.message(Command("tasks"))
async def tasks(message: types.Message, dialog_manager: DialogManager, state: FSMContext,) -> None:
    await state.clear()

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


@router.message(Command("add_notify"))
async def add_notify(message: types.Message) -> None:
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "ℹ️ Формат команды:\n"
            "<code>/add_notify Текст задачи 2026-12-31</code>"
        )
        return

    data, _, raw_date = args[1].rpartition(" ")
    if not data.strip():
        await message.answer(
            "⚠️ Не хватает текста задачи.\n"
            "Формат: <code>/add_notify Текст задачи 2026-12-31</code>"
        )
        return

    try:
        deadline = datetime.fromisoformat(raw_date.strip()).date()
    except ValueError:
        await message.answer(
            "⚠️ Не получилось разобрать дату.\n"
            "Используйте формат <code>ГГГГ-ММ-ДД</code>, "
            "например <code>2026-12-31</code>."
        )
        return

    bd = BotBD()
    try:
        _ensure_user(bd, message.from_user)
        bd.add_notification(message.from_user.id, data.strip(), deadline)
    finally:
        bd.close_connection()

    await message.answer(
        "✅ <b>Задача добавлена!</b>\n"
        f"{DIVIDER}\n\n"
        f"📝 {escape(data.strip())}\n"
        f"📅 Дедлайн: <b>{deadline.strftime('%d.%m.%Y')}</b>"
    )


@router.message(Command("get_notifications"))
async def get_notify(message: types.Message) -> None:
    bd = BotBD()
    try:
        rows = bd.get_user_notifications(message.from_user.id)
    finally:
        bd.close_connection()

    rows = sorted(rows, key=lambda row: (row[3], str(row[2])))

    if not rows:
        await message.answer("✨ Задач пока нет.")
        return

    lines = [f"🕒 <b>Ваши задачи</b>\n{DIVIDER}"]
    for _, text, date_str, status in rows:
        try:
            date_str = datetime.fromisoformat(str(date_str)).strftime("%d.%m.%Y")
        except ValueError:
            pass
        icon = "✅" if status == 1 else "🟢"
        lines.append(f"{icon} {escape(str(date_str))} — {escape(str(text))}")

    await message.answer("\n".join(lines))
