from aiogram import Router

from .main_router import router as main_router
from .KeyboardCallbacks import router as callbacks_router
from .reminders import router as reminders_router

routers = Router()
routers.include_routers(main_router, callbacks_router, reminders_router)
