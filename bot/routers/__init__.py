from .main_router import router as main_router
from .KeyboardCallbacks import router as callbacks_router
from aiogram import Router

routers = Router()
routers.include_routers(main_router, callbacks_router)
