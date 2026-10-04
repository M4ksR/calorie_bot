from aiogram.utils.keyboard import InlineKeyboardBuilder

def add_food_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text="Сохраненные блюда", callback_data="save_food")
    builder.button(text="Поиск продукта", callback_data="find_food")
    builder.button(text="Свое блюдо", callback_data="my_food")
    builder.button(text="Назад", callback_data="back")

    builder.adjust(1)
    return builder.as_markup()

def start_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text="Дневная норма", callback_data="DailyAllowance")
    builder.button(text="Добавить еду", callback_data="builder")
    builder.button(text="Осталось", callback_data="LeftCalories")
    builder.button(text="Удалить еду", callback_data="DeleteFood")

    builder.adjust(2)
    return builder.as_markup()
