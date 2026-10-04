from aiogram.fsm.state import State, StatesGroup

class CustomFood(StatesGroup):
    waiting_for_name_of_food = State()
    waiting_for_kbju = State()
    waiting_for_weight = State()
