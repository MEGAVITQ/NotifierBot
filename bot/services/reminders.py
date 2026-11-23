import asyncio
import logging
from datetime import date, datetime, timedelta, timezone
from html import escape
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database import BotBD

logger = logging.getLogger(__name__)

try:
    TIMEZONE = ZoneInfo("Europe/Moscow")
except ZoneInfoNotFoundError:  # на случай отсутствия tzdata в системе
    TIMEZONE = timezone(timedelta(hours=3), name="MSK")
REMINDER_HOUR = 8          # напоминания уходят с 08:00 по Москве
CHECK_INTERVAL = 60        # проверять базу раз в минуту

DIVIDER = "━━━━━━━━━━━━━━━━━━"

# Сколько дней осталось до дедлайна -> вид напоминания
STAGES = {3: "3d", 1: "1d", 0: "0d"}


def _days_word(number: int) -> str:
    """1 день / 2 дня / 5 дней."""
    number = abs(number)
    if number % 10 == 1 and number % 100 != 11:
        return "день"
    if 2 <= number % 10 <= 4 and not 12 <= number % 100 <= 14:
        return "дня"
    return "дней"


def _render_text(kind: str, task_data: str, deadline: date, days_left: int) -> str:
    task_data = escape(task_data)
    deadline_str = deadline.strftime("%d.%m.%Y")

    if kind == "3d":
        return (
            "🔔 <b>Напоминание о задаче</b>\n"
            f"{DIVIDER}\n\n"
            f"📝 {task_data}\n"
            f"📅 Дедлайн: <b>{deadline_str}</b>\n"
            "⏳ До дедлайна осталось <b>3 дня</b>."
        )

    if kind == "1d":
        return (
            "🔔 <b>Напоминание о задаче</b>\n"
            f"{DIVIDER}\n\n"
            f"📝 {task_data}\n"
            f"📅 Дедлайн: <b>{deadline_str}</b>\n"
            "⏳ Остался <b>1 день</b>."
        )

    if kind == "0d":
        return (
            "🔔 <b>Напоминание о задаче</b>\n"
            f"{DIVIDER}\n\n"
            f"📝 {task_data}\n"
            f"📅 Дедлайн: <b>сегодня, {deadline_str}</b>\n"
            "🔥 <b>Последний день — самое время выполнить!</b>"
        )

    # overdue
    days = abs(days_left)
    return (
        "⚠️ <b>Задача просрочена</b>\n"
        f"{DIVIDER}\n\n"
        f"📝 {task_data}\n"
        f"📅 Дедлайн был: <b>{deadline_str}</b>\n"
        f"❗️ Просрочено на <b>{days} {_days_word(days)}</b>.\n\n"
        "Отметьте задачу выполненной или вернитесь к ней в списке."
    )


def _keyboard(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Отметить выполненной",
                callback_data=f"task_done:{task_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📋 Мои задачи",
                callback_data="open_tasks",
            ),
        ],
    ])


async def send_due_reminders(bot: Bot) -> None:
    """Один проход: отправить все напоминания, время которых наступило."""
    now = datetime.now(TIMEZONE)
    if now.hour < REMINDER_HOUR:
        return

    bd = BotBD()
    try:
        pending = bd.get_pending_notifications()
        sent = bd.get_sent_reminders()

        for task_id, user_id, task_data, date_str in pending:
            try:
                deadline = date.fromisoformat(str(date_str))
            except ValueError:
                logger.warning("Задача %s: некорректная дата %r", task_id, date_str)
                continue

            days_left = (deadline - now.date()).days
            kind = "overdue" if days_left < 0 else STAGES.get(days_left)
            if kind is None or kind in sent.get(task_id, set()):
                continue

            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=_render_text(kind, task_data, deadline, days_left),
                    reply_markup=_keyboard(task_id),
                )
            except (TelegramForbiddenError, TelegramBadRequest) as error:
                logger.warning(
                    "Не удалось отправить напоминание по задаче %s пользователю %s: %s",
                    task_id, user_id, error,
                )
                # Постоянная ошибка (бот заблокирован / чат недоступен):
                # помечаем, чтобы не пытаться каждую минуту.
                bd.mark_reminder_sent(task_id, kind)
                continue
            except Exception:
                logger.exception(
                    "Ошибка при отправке напоминания по задаче %s", task_id,
                )
                continue

            bd.mark_reminder_sent(task_id, kind)
            logger.info("Напоминание %s по задаче %s отправлено", kind, task_id)
    finally:
        bd.close_connection()


async def reminder_worker(bot: Bot) -> None:
    """Фоновый цикл напоминаний (запускается при старте бота)."""
    logger.info("Планировщик напоминаний запущен (Москва, %02d:00)", REMINDER_HOUR)
    while True:
        try:
            await send_due_reminders(bot)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Планировщик напоминаний упал, повтор через минуту")
        await asyncio.sleep(CHECK_INTERVAL)
