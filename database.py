import aiosqlite
import re
import unicodedata

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

MOSCOW = ZoneInfo("Europe/Moscow")

async def init_database():
    async with aiosqlite.connect("calorie_bot.db") as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS food_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                food_name TEXT NOT NULL,
                weight REAL NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                fat REAL NOT NULL,
                carbs REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                daily_calories REAL NOT NULL,
                daily_protein REAL NOT NULL,
                daily_fat REAL NOT NULL,
                daily_carbs REAL NOT NULL,
                streak INTEGER NOT NULL DEFAULT 0,
                last_active_date TEXT
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_food (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                food_name TEXT NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                fat REAL NOT NULL,
                carbs REAL NOT NULL
            )
            """
        )
        await db.commit()

    async with aiosqlite.connect("data/basic_foods.db") as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS basic_foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_ru TEXT NOT NULL,
                name_normalized TEXT NOT NULL,
                name_en TEXT,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                fat REAL NOT NULL,
                carbs REAL NOT NULL,
                usda_id INTEGER, 
                UNIQUE (name_normalized, usda_id)
            )
            """
        )
        await db.commit()

async def add_food_entry(user_id,
                         food_name,
                         weight,
                         calories,
                         protein,
                         fat,
                         carbs):
    async with aiosqlite.connect("calorie_bot.db") as db:
        await db.execute(
            """
            INSERT INTO food_entries (
                user_id,
                food_name,
                weight,
                calories,
                protein,
                fat,
                carbs
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                food_name,
                weight,
                calories,
                protein,
                fat,
                carbs
            )
        )
        await db.commit()

async def set_daily_calories(user_id,
                             daily_calories,
                             daily_protein,
                             daily_fat,
                             daily_carbs):
    async with aiosqlite.connect("calorie_bot.db") as db:
        await db.execute(
            """
            INSERT INTO users (user_id, daily_calories, daily_protein, daily_fat, daily_carbs) 
            VALUES (?, ?, ?, ?, ?)
                
            ON CONFLICT (user_id)
            DO UPDATE SET 
                daily_calories = excluded.daily_calories,
                daily_protein = excluded.daily_protein,
                daily_fat = excluded.daily_fat,
                daily_carbs = excluded.daily_carbs
            """,
            (
                user_id,
                daily_calories,
                daily_protein,
                daily_fat,
                daily_carbs
            )
        )
        await db.commit()

async def get_daily_calories(user_id):
    async with aiosqlite.connect("calorie_bot.db") as db:
        cursor = await db.execute(
            """
            SELECT daily_calories, daily_protein, daily_fat, daily_carbs
            FROM users
            WHERE user_id = ?
            """,
            (
                user_id,
            )
        )
        row = await cursor.fetchone()
        return None if not row else row

async def get_today_calories(user_id, current_date=None):
    async with aiosqlite.connect("calorie_bot.db") as db:
        DT = datetime.now(MOSCOW).date() if current_date is None else current_date
        start, end = get_day_bounds_utc(DT)
        cursor = await db.execute(
            """
            SELECT 
                COALESCE(SUM(calories), 0), 
                COALESCE(SUM(protein), 0), 
                COALESCE(SUM(fat), 0), 
                COALESCE(SUM(carbs), 0) 
            FROM food_entries
            WHERE user_id = ?
            AND created_at >= ?
            AND created_at < ?
            """,
            (
            user_id,
            start,
            end
            )
        )
        row = await cursor.fetchone()
        return row

async def get_today_food_entries(user_id):
    async with aiosqlite.connect("calorie_bot.db") as db:
        today = datetime.now(MOSCOW).date()
        start, end = get_day_bounds_utc(today)
        cursor = await db.execute(
            """
            SELECT id, food_name, weight, calories
            FROM food_entries
            WHERE user_id = ?
            AND created_at >= ?
            AND created_at < ?
            """,
            (
                user_id,
                start,
                end
            )
        )
        return await cursor.fetchall()

async def delete_food_entry(entry_id, user_id):
    async with aiosqlite.connect("calorie_bot.db") as db:
        await db.execute(
            """
            DELETE FROM food_entries
            WHERE id = ? AND user_id = ?
            """,
            (
                entry_id,
                user_id
            )
        )
        await db.commit()

async def save_food(user_id, food_name, calories, protein, fat, carbs):
    async with aiosqlite.connect("calorie_bot.db") as db:
        await db.execute(
            """
            INSERT INTO saved_food (user_id,
                                    food_name,
                                    calories,
                                    protein,
                                    fat,
                                    carbs)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                food_name,
                calories,
                protein,
                fat,
                carbs
            )
        )
        await db.commit()

async def get_saved_food(user_id):
    async with aiosqlite.connect("calorie_bot.db") as db:
        cursor = await db.execute(
            """
            SELECT id, food_name, calories, protein, fat, carbs
            FROM saved_food
            WHERE user_id = ?
            """,
            (
                user_id,
            )
        )
        return await cursor.fetchall()

async def get_saved_food_by_id(food_id, user_id):
    async with aiosqlite.connect("calorie_bot.db") as db:
        cursor = await db.execute(
            """
            SELECT food_name, calories, protein, fat, carbs FROM saved_food
            WHERE id = ?
            AND user_id = ?
            """,
            (
                food_id,
                user_id
            )
        )
        return await cursor.fetchone()

async def delete_saved_food_by_id(food_id, user_id):
    async with aiosqlite.connect("calorie_bot.db") as db:
        await db.execute(
            """
            DELETE FROM saved_food 
            WHERE id = ? AND user_id = ?
            """,
            (
                food_id, user_id
            )
        )
        await db.commit()

def get_day_bounds_utc(selected_date):
    start_msk = datetime.combine(selected_date, time.min, tzinfo=MOSCOW)
    end_msk = start_msk + timedelta(days=1)

    start_utc = start_msk.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    end_utc = end_msk.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    return start_utc, end_utc

async def get_food_entries_by_date(user_id, selected_date):
    async with aiosqlite.connect("calorie_bot.db") as db:
        start_utc, end_utc = get_day_bounds_utc(selected_date)
        cursor = await db.execute(
            """
            SELECT food_name, weight, calories, protein, fat, carbs FROM food_entries
            WHERE user_id = ?
            AND created_at >= ?
            AND created_at < ?
            ORDER BY created_at
            """,
            (
                user_id,
                start_utc,
                end_utc
            )
        )
        return await cursor.fetchall()

async def delete_old_food_entries(cutoff_datetime):
    async with aiosqlite.connect("calorie_bot.db") as db:
        await db.execute(
            """
            DELETE FROM food_entries
            WHERE created_at < ?
            """,
            (
                cutoff_datetime,
            )
        )
        await db.commit()

SEARCH_ALIASES = {
    "курица": ["курица", "курин", "цыплен", "цыплят", "бройлер"],
    "творог": ["творог", "творож"],
    "говядина": ["говядин", "говяж"],
    "свинина": ["свинин", "свин"],
    "индейка": ["индейк", "индюш"]
}

PREPARED_FOOD_WORDS = [
    "соус",
    "лапш",
    "рис",
    "греч",
    "наггет",
    "котлет",
    "тефтел",
    "пюре",
    "грил",
    "шашлы",
    "попкорн",
    "олад",
    "ролл",
    "салат",
    "суп",
    "паштет",
    "пельмен",
    "сэндвич",
    "бургер",
    "хот дог",
    "маринад",
    "паниров",
    "терияки",
    "тушен",
    "варен",
    "жарен",
    "запеч",
    "копчен",
    "сгущ",
    "быстрозаморож",
    "стритс",
    "люля",
    "рулет",
    "ветчин",
    "фрикадел",
    "шницел",
    "зраз",
    "сосиск",
    "сардел",
    "колбас",
    "яйц",
    "бульон",
    "онигири",
    "чиабат",
    "кордон",
    "криспи",
    "гриб",
    "картоф",
    "бекон",
    "начинк",
    "спагет",
    "овощ",
    "рап"
]

def normalize_product_search(query):
    query = unicodedata.normalize("NFKC", query)
    query = query.casefold().replace("ё", "е")
    query = re.sub(r"(?<=\d),(?=\d)", ".", query)
    query = query.replace("%", "")
    query = re.sub(r"[^0-9a-zа-я.+]+", " ", query)
    query = re.sub(r"\s+", " ", query).strip()
    return query

def build_fts_query(query):
    words = normalize_product_search(query).split()
    if not words: return None

    result = []
    for word in words:
        variants = SEARCH_ALIASES.get(word, [word])
        if len(variants) == 1:
            result.append(f'"{word}"*')
        else:
            variants_query = " OR ".join(f'"{variant}"*' for variant in variants)
            result.append(f"({variants_query})")

    return " AND ".join(result)

def product_search_score(product, food_name):
    name = normalize_product_search(product["name"])
    query = normalize_product_search(food_name)

    name_words = name.split()
    query_words = query.split()

    prepared_penalty = 0
    for prepared_word in PREPARED_FOOD_WORDS:
        if prepared_word in name and prepared_word not in query:
            prepared_penalty += 1

    if len(query_words) == 1:
        full_name = f" {name} "
        if " с " in full_name or " в " in full_name or " под " in full_name:
            prepared_penalty += 1

    if name == query:
        match_priority = 0
    elif name.startswith(query):
        match_priority = 1
    elif query in name:
        match_priority = 2
    else:
        match_priority = 3

    source_priority = {
        "magnit": 1,
        "lenta": 2,
        "usda": 3
    }.get(product["source"], 4)

    if len(query_words) == 1:
        return prepared_penalty, source_priority, match_priority, len(name_words), len(name)

    return match_priority, prepared_penalty, source_priority, len(name_words), len(name)

async def search_products(food_name, page=0, page_size=5):
    fts_query = build_fts_query(food_name)
    if not fts_query: return [], 0

    async with aiosqlite.connect("data/products.db") as db:
        cursor = await db.execute(
            """
            SELECT p.id,
                   p.source,
                   p.source_id,
                   p.name,
                   p.brand,
                   p.calories,
                   p.protein,
                   p.fat,
                   p.carbs,
                   p.weight,
                   p.weight_unit,
                   p.url,
                   p.image_url
            FROM products_fts JOIN products p
            ON p.id = products_fts.rowid
            WHERE products_fts MATCH ?
            """,
            (
                fts_query,
            )
        )

        rows = await cursor.fetchall()
        result = []
        for row in rows:
            product = {
                "id": row[0],
                "source": row[1],
                "source_id": row[2],
                "name": row[3],
                "brand": row[4],
                "calories": row[5],
                "protein": row[6],
                "fat": row[7],
                "carbs": row[8],
                "weight": row[9],
                "weight_unit": row[10],
                "url": row[11],
                "image_url": row[12]
            }
            result.append(product)

    result.sort(key=lambda product: product_search_score(product, food_name))

    total = len(result)
    start = page * page_size
    end = start + page_size

    return result[start:end], total

async def ensure_user(user_id):
    async with aiosqlite.connect("calorie_bot.db") as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users (user_id,
                                        daily_calories,
                                        daily_protein,
                                        daily_fat,
                                        daily_carbs,
                                        streak,
                                        last_active_date)
            VALUES (?, 0, 0, 0, 0, 0, NULL)
            """,
            (
                user_id,
            )
        )
        await db.commit()

async def update_streak(user_id):
    await ensure_user(user_id)
    today = datetime.now(MOSCOW).date()
    yesterday = (today - timedelta(days=1))

    today = today.isoformat()
    yesterday = yesterday.isoformat()

    async with aiosqlite.connect("calorie_bot.db") as db:
        cursor = await db.execute(
            """
            SELECT streak, last_active_date
            FROM users
            WHERE user_id = ?
            """,
            (
                user_id,
            )
        )
        row = await cursor.fetchone()

        streak = row[0]
        last_active_date = row[1]

        if last_active_date == today:
            pass
        elif last_active_date == yesterday:
            streak += 1
        else:
            streak = 1

        await db.execute(
            """
            UPDATE users
            SET streak = ?, last_active_date = ?
            WHERE user_id = ?
            """,
            (
                streak,
                today,
                user_id
            )
        )

        await db.commit()
        return streak

async def add_food_and_update_streak(user_id,
                                     food_name,
                                     weight,
                                     calories,
                                     protein,
                                     fat,
                                     carbs):

    await add_food_entry(user_id, food_name, weight, calories, protein, fat, carbs)
    await update_streak(user_id)

async def get_user_streak(user_id):
    async with aiosqlite.connect("calorie_bot.db") as db:
        cursor = await db.execute(
            """
            SELECT streak 
            FROM users 
            WHERE user_id = ?
            """,
            (
                user_id,
            )
        )
        row = await cursor.fetchone()
        return 0 if row is None else row[0]

async def get_dashboard_data(user_id):
    await ensure_user(user_id)
    daily = await get_daily_calories(user_id)
    eaten = await get_today_calories(user_id)
    streak = await get_user_streak(user_id)
    return {
        "daily": {
            "calories": daily[0],
            "protein": daily[1],
            "fat": daily[2],
            "carbs": daily[3]
        },
        "eaten": {
            "calories": eaten[0],
            "protein": eaten[1],
            "fat": eaten[2],
            "carbs": eaten[3]
        },
        "left": {
            "calories": daily[0] - eaten[0],
            "protein": daily[1] - eaten[1],
            "fat": daily[2] - eaten[2],
            "carbs": daily[3] - eaten[3]
        },
        "streak": streak
    }

async def get_weekly_calories(user_id):
    current_date = datetime.now(MOSCOW).date()
    result = []
    for days in range(-6, 1):
        select_date = current_date + timedelta(days=days)
        calories = await get_today_calories(user_id, select_date)
        result.append({"date": select_date.isoformat(), "calories": calories[0]})
    return result
