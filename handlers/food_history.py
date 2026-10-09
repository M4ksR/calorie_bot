from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards import WEEKDAYS, history
from database import get_today_calories, get_food_entries_by_date

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

router = Router()

@router.callback_query(F.data.startswith("FoodHistory"))
async def food_history_handler(callback: CallbackQuery) -> None:
    await callback.answer()

    splt = callback.data.split('_')
    offset = int(splt[1]) if len(splt) > 1 else 0
    calories = [await get_today_calories(callback.from_user.id, day)
                for day in [datetime.now(ZoneInfo("Europe/Moscow")).date() + timedelta(days=off) for off in range(-6,1)]]

    selected_date = datetime.now(ZoneInfo("Europe/Moscow")).date() + timedelta(days=offset)
    data = await get_food_entries_by_date(callback.from_user.id, selected_date)

    if not data:
        await callback.message.edit_text("За сегодня не было добавлено ни одного блюда",
                                         reply_markup=history(calories))
        return

    weekday = WEEKDAYS[selected_date.weekday()]
    date_text = selected_date.strftime("%d.%m")
    tcalories = tprotein = tfat = tcarbs = 0

    for food_entry in data:
        tcalories += food_entry[2]
        tprotein += food_entry[3]
        tfat += food_entry[4]
        tcarbs += food_entry[5]

    text = [f"<b>Итоги дня - {weekday} {date_text}</b>\n"
        f"<pre>"
        f"{'Калории':<10}"
        f"{'Белки':<9}"
        f"{'Жиры':<8}"
        f"{'Углеводы':<10}\n"
        f"{tcalories:<10.1f}"
        f"{tprotein:<9.1f}"
        f"{tfat:<8.1f}"
        f"{tcarbs:<10.1f}"
        f"</pre>"]

    for food_entry in data:
        text.append(
            f"<b>{food_entry[0]}</b> — {food_entry[1]:.0f} г\n"
            f"<pre>"
            f"{'Калории':<10}"
            f"{'Белки':<9}"
            f"{'Жиры':<8}"
            f"{'Углеводы':<10}\n"
            f"{food_entry[2]:<10.1f}"
            f"{food_entry[3]:<9.1f}"
            f"{food_entry[4]:<8.1f}"
            f"{food_entry[5]:<10.1f}"
            f"</pre>"
        )

    await callback.message.edit_text( "\n\n".join(text),
                                      reply_markup=history(calories),
                                      parse_mode="HTML")
