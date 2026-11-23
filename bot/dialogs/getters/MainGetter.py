from aiogram_dialog import DialogManager
from bot.database import BotBD

async def main_getter(dialog_manager: DialogManager, **middleware_data):
    bd = BotBD()
    notifications = bd.get_user_notifications(dialog_manager.start_data.get("user_id"))
    bd.close_connection()
    return {"tasks": notifications}
