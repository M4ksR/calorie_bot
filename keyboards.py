from aiogram.utils.keyboard import InlineKeyboardBuilder

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

def saved_food_menu(data):
    builder = InlineKeyboardBuilder()

    for food in data:
        builder.button(text=f"{food[1]} - {food[2]:.0f} ккал", callback_data=f"saved_food_{food[0]}")

    builder.button(text="↩️Назад", callback_data="back")

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
        builder.button(text=f"{weekday} - {date_text} - {calories[offset + 6]:.0f} ккал", callback_data=f"FoodHistory_{offset}")

    builder.button(text="↩️Назад", callback_data="back")
    builder.adjust(1)

    return builder.as_markup()

def delete_food_menu(data):
    builder = InlineKeyboardBuilder()
    for i in data:
        builder.button(text=f"{i[1]} - {i[2]}г - {i[3]:.0f}ккал", callback_data=f"delete_food_{i[0]}")

    builder.button(text="↩️Назад", callback_data="back")
    builder.adjust(1)

    return builder.as_markup()

def purpose():
    builder = InlineKeyboardBuilder()

    builder.button(text="Снижение веса", callback_data="WeightLoss")
    builder.button(text="Поддержание веса", callback_data="WeightMaintenance")
    builder.button(text="Увеличение веса", callback_data="WeightGain")

    builder.adjust(1)
    return builder.as_markup()

def activity():
    builder = InlineKeyboardBuilder()

    builder.button(text="Сидячий образ жизни", callback_data="Sit")
    builder.button(text="Легкая активность", callback_data="Lite")
    builder.button(text="Умеренная активность", callback_data="Medium")
    builder.button(text="Высокая активность", callback_data="Hard")

    builder.adjust(1)
    return builder.as_markup()

def gender():
    builder = InlineKeyboardBuilder()

    builder.button(text="Мужчина", callback_data="Male")
    builder.button(text="Женщина", callback_data="Female")

    builder.adjust(2)
    return builder.as_markup()

def calculation_of_daily_allowance():
    builder = InlineKeyboardBuilder()

    builder.button(text="Рассчитать норму", callback_data="Calculate_daily")
    builder.button(text="Узнать норму", callback_data="Find_out_daily")
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

    builder.button(text="Сохраненные блюда", callback_data="save_food")
    builder.button(text="Поиск продукта", callback_data="find_food")
    builder.button(text="Свое блюдо", callback_data="my_food")
    builder.button(text="↩️Назад", callback_data="back")

    builder.adjust(1)
    return builder.as_markup()

def start_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text="Дневная норма", callback_data="DailyAllowance")
    builder.button(text="Добавить еду", callback_data="AddFood")
    builder.button(text="Осталось", callback_data="LeftCalories")
    builder.button(text="Удалить еду", callback_data="DeleteFood")
    builder.button(text="📋История питания", callback_data="FoodHistory")

    builder.adjust(2)
    return builder.as_markup()
