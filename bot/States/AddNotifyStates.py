from aiogram.fsm.state import State, StatesGroup

class AddNotifyStates(StatesGroup):
    ASK_DATA = State()
    ASK_DATE = State()