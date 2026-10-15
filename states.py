from aiogram.fsm.state import State, StatesGroup

class CustomFood(StatesGroup):
    waiting_for_name_of_food = State()
    waiting_for_kbju = State()
    waiting_for_weight = State()

class DailyAllowance(StatesGroup):
    waiting_for_gender = State()
    waiting_for_weight = State()
    waiting_for_height = State()
    waiting_for_age = State()
    waiting_for_activity = State()
    waiting_for_purpose = State()

class SavedFood(StatesGroup):
    waiting_for_weight = State()
    waiting_for_confirm = State()

class ProductSearch(StatesGroup):
    waiting_for_product = State()
    waiting_for_weight = State()
    waiting_for_confirm = State()

class AiFood(StatesGroup):
    waiting_for_food_list = State()
    waiting_for_confirm = State()
