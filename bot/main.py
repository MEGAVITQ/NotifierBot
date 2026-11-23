from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .misc import TgKeys
from aiogram.client.default import DefaultBotProperties

TgKeys = TgKeys()
token = TgKeys.get_token()

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML, ))
dp = Dispatcher(storage=MemoryStorage())