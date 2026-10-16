import aiosqlite

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pydantic.v1.json import isoformat


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

async def get_today_calories(user_id, current_date="now"):
    async with aiosqlite.connect("calorie_bot.db") as db:
        cursor = await db.execute(
            """
            SELECT 
                COALESCE(SUM(calories), 0), 
                COALESCE(SUM(protein), 0), 
                COALESCE(SUM(fat), 0), 
                COALESCE(SUM(carbs), 0) 
            FROM food_entries
            WHERE user_id = ?
            AND DATE(created_at) = DATE(?)
            """,
            (
            user_id,
            current_date
            )
        )
        row = await cursor.fetchone()
        return row

async def get_today_food_entries(user_id):
    async with aiosqlite.connect("calorie_bot.db") as db:
        cursor = await db.execute(
            """
            SELECT id, food_name, weight, calories
            FROM food_entries
            WHERE user_id = ?
            AND DATE(created_at) = DATE('now')
            """,
            (
                user_id,
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

async def get_food_entries_by_date(user_id, selected_date):
    async with aiosqlite.connect("calorie_bot.db") as db:
        cursor = await db.execute(
            """
            SELECT food_name, weight, calories, protein, fat, carbs FROM food_entries
            WHERE user_id = ?
            AND DATE(created_at) = ?
            ORDER BY created_at
            """,
            (
                user_id,
                selected_date
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

def normalize_search_words(query):
    return query.casefold().replace(',', ' ').split()

def product_score(product_name, query):
    product_name = product_name.casefold()
    products_words = normalize_search_words(product_name)
    full_query = " ".join(query)
    if products_words == query: return 0
    if products_words[:len(query)] == query: return 1
    if full_query in product_name: return 2
    if all(word in products_words for word in query): return 3
    return 4

async def search_basic_foods(food_name, limit=20):
    async with aiosqlite.connect("data/basic_foods.db") as db:
        words = normalize_search_words(food_name)
        if not words: return []

        params = tuple(f"%{word}%" for word in words)
        conditions = " AND ".join(["name_normalized LIKE ?"] * len(words))

        cursor = await db.execute(
            f"""
                SELECT name_ru, calories, protein, fat, carbs 
                FROM basic_foods
                WHERE {conditions}
            """,
            params
        )

        result = []
        rows = await cursor.fetchall()

        rows.sort(key=lambda row: (product_score(row[0], words), len(row[0])))
        rows = rows[:limit]

        for row in rows:
            food = {
                "name": row[0],
                "brand": None,
                "calories": row[1],
                "protein": row[2],
                "fat": row[3],
                "carbs": row[4],
                "source": "local",
                "url": None
            }
            result.append(food)

        return result

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
    today = datetime.now(ZoneInfo("Europe/Moscow")).date()
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
