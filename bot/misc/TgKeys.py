import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

TOKEN_KEYS = ("BOT_TOKEN", "TOKEN")
TOKEN_RE = re.compile(r"^\d{5,}:[A-Za-z0-9_-]{30,}$")


def _clean(value: str | None) -> str:
    return (value or "").strip().strip("\"'").strip()


def _mask(token: str) -> str:
    if len(token) <= 8:
        return "***"
    return f"{token[:4]}...{token[-4:]} (len={len(token)})"


class TgKeys:
    def __init__(self):
        env_before = {key: _clean(os.getenv(key)) for key in TOKEN_KEYS}

        # Читаем .env от корня проекта, независимо от текущей рабочей папки.
        # override=True: файл .env считаем главным источником, если он есть.
        load_dotenv(dotenv_path=ENV_FILE, override=True)

        token = ""
        for key in TOKEN_KEYS:
            token = _clean(os.getenv(key))
            if token:
                break

        if not token:
            raise RuntimeError(
                "Telegram TOKEN не найден. Создайте файл "
                f"{ENV_FILE} со строкой:\n"
                "TOKEN=123456789:AAExampleTokenFromBotFather"
            )

        if not TOKEN_RE.fullmatch(token):
            raise RuntimeError(
                "Telegram TOKEN имеет неверный формат: "
                f"{_mask(token)}. Ожидается '<id>:<секрет>' без кавычек "
                "и пробелов. Возможно, в переменной окружения TOKEN лежит "
                "значение от другого сервиса."
            )

        changed_by_env = next(
            (
                key for key in TOKEN_KEYS
                if env_before[key] and env_before[key] != token
            ),
            None,
        )
        if changed_by_env:
            logger.warning(
                "Переменная окружения %s отличалась от %s — "
                "использую значение из .env",
                changed_by_env, ENV_FILE,
            )

        self.token = token

    def get_token(self):
        return self.token
