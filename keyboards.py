from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

WEEKDAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье"
]

def confirm_aifood():
    builder = InlineKeyboardBuilder()

    builder.button(text="✅Добавить", callback_data="confirm_aifood")
    builder.button(text="❌Отменить", callback_data="cancel_aifood")
    builder.adjust(2)

    return builder.as_markup()

def cancel_daily_allowance():
    builder = InlineKeyboardBuilder()
    builder.button(text="↩️Назад", callback_data="cancel_daily_allowance")
    return builder.as_markup()

def cancel_add_food():
    builder = InlineKeyboardBuilder()
    builder.button(text="↩️Назад", callback_data="cancel_add_food")
    return builder.as_markup()

def go_to_start_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🪟Стартовое меню", callback_data="go_to_start_menu")
    return builder.as_markup()

def confirm_search_food():
    builder = InlineKeyboardBuilder()

    builder.button(text="✅Добавить", callback_data="confirm_search_food")
    builder.button(text="❌Отменить", callback_data="cancel_search_food")
    builder.adjust(2)

    return builder.as_markup()

def products_search_menu(products, page=0):
    start = page * 5
    end = min(start + 5, len(products))

    builder = InlineKeyboardBuilder()
    for i in range(start, end):
        builder.button(text=f"{products[i].get('name')} | {products[i].get('brand - ', "")}{products[i].get('calories'):.1f}ккал",
                       callback_data=f"product_select_{i}")

    builder.button(text="↩️Назад", callback_data="cancel_add_food")
    builder.adjust(1)

    buttons = []
    if page != 0:
        buttons.append(InlineKeyboardButton(text="◀️пред",
                                            callback_data=f"product_page_{page-1}"))
    if end < len(products):
        buttons.append(InlineKeyboardButton(text="след▶️",
                                            callback_data=f"product_page_{page+1}"))
    builder.row(*buttons)
    return builder.as_markup()

def saved_food_menu(data):
    builder = InlineKeyboardBuilder()

    for food in data:
        builder.button(text=f"{food[1]} - {food[2]:.1f} ккал", callback_data=f"saved_food_{food[0]}")
    builder.adjust(1)

    builder.row(
        InlineKeyboardButton(text="🗑️Удалить", callback_data="delete_saved_food"),
        InlineKeyboardButton(text="↩️Назад", callback_data="cancel_add_food")
    )

    return builder.as_markup()

def delete_saved_food(data):
    builder = InlineKeyboardBuilder()

    for food in data:
        builder.button(text=f"{food[1]} - {food[2]:.1f} ккал", callback_data=f"delete_saved_food_{food[0]}")

    builder.button(text="↩️Назад", callback_data="cancel_delete_food")
    builder.adjust(1)

    return builder.as_markup()


def history(calories):
    builder = InlineKeyboardBuilder()

    msk = ZoneInfo("Europe/Moscow")
    today = datetime.now(msk).date()

    for offset in range(-6,1):
        curr_date = today + timedelta(days=offset)
        weekday = WEEKDAYS[curr_date.weekday()]
        date_text = curr_date.strftime("%d.%m")
        builder.button(text=f"{weekday} - {date_text} - {calories[offset + 6]:.1f} ккал", callback_data=f"FoodHistory_{offset}")

    builder.button(text="↩️Назад", callback_data="back")
    builder.adjust(1)

    return builder.as_markup()

def delete_food_menu(data):
    builder = InlineKeyboardBuilder()
    for i in data:
        builder.button(text=f"{i[1]} - {i[2]}г - {i[3]:.1f}ккал", callback_data=f"delete_food_{i[0]}")

    builder.button(text="↩️Назад", callback_data="back")
    builder.adjust(1)

    return builder.as_markup()

def purpose():
    builder = InlineKeyboardBuilder()

    builder.button(text="📉Снижение веса", callback_data="WeightLoss")
    builder.button(text="⚖️Поддержание веса", callback_data="WeightMaintenance")
    builder.button(text="📈Увеличение веса", callback_data="WeightGain")
    builder.button(text="↩️Назад", callback_data="cancel_daily_allowance")

    builder.adjust(1)
    return builder.as_markup()

def activity():
    builder = InlineKeyboardBuilder()

    builder.button(text="🪑Сидячий образ жизни", callback_data="Sit")
    builder.button(text="🚶Легкая активность", callback_data="Lite")
    builder.button(text="🏃Умеренная активность", callback_data="Medium")
    builder.button(text="🏋️Высокая активность", callback_data="Hard")
    builder.button(text="↩️Назад", callback_data="cancel_daily_allowance")

    builder.adjust(1)
    return builder.as_markup()

def gender():
    builder = InlineKeyboardBuilder()

    builder.button(text="👨Мужчина", callback_data="Male")
    builder.button(text="👩Женщина", callback_data="Female")
    builder.button(text="↩️️Назад", callback_data="cancel_daily_allowance")

    builder.adjust(2)
    return builder.as_markup()

def calculation_of_daily_allowance():
    builder = InlineKeyboardBuilder()

    builder.button(text="📱Рассчитать норму", callback_data="Calculate_daily")
    builder.button(text="📊Узнать норму", callback_data="Find_out_daily")
    builder.button(text="↩️Назад", callback_data="Back_daily")

    builder.adjust(1)
    return builder.as_markup()

def confirm_custom_food():
    builder = InlineKeyboardBuilder()

    builder.button(text="✅Добавить", callback_data="confirm_food")
    builder.button(text="⭐Добавить и Сохранить", callback_data="confirm_and_save_food")
    builder.button(text="❌Отменить", callback_data="cancel_food")

    builder.adjust(1)
    return builder.as_markup()

def add_food_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text="⭐Сохраненные блюда", callback_data="save_food")
    builder.button(text="🔎Поиск продукта", callback_data="find_food")
    builder.button(text="✍️Свое блюдо", callback_data="my_food")
    builder.button(text="⚡Быстрый подсчёт", callback_data="quick_calculation")
    builder.button(text="↩️Назад", callback_data="back")

    builder.adjust(1)
    return builder.as_markup()

def start_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text="🎯Дневная норма", callback_data="DailyAllowance")
    builder.button(text="🍽️Добавить еду", callback_data="AddFood")
    builder.button(text="🔥Осталось", callback_data="LeftCalories")
    builder.button(text="🗑️Удалить еду", callback_data="DeleteFood")
    builder.button(text="📋История питания", callback_data="FoodHistory")

    builder.adjust(2)
    return builder.as_markup()
