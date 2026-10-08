import aiosqlite

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
                daily_calories INTEGER NOT NULL
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

async def set_daily_calories(user_id, daily_calories):
    async with aiosqlite.connect("calorie_bot.db") as db:
        await db.execute(
            """
            INSERT INTO users (user_id, daily_calories) 
            VALUES (?, ?)
                
            ON CONFLICT (user_id)
            DO UPDATE SET daily_calories = excluded.daily_calories
            """,
            (
                user_id,
                daily_calories
            )
        )
        await db.commit()

async def get_daily_calories(user_id):
    async with aiosqlite.connect("calorie_bot.db") as db:
        cursor = await db.execute(
            """
            SELECT daily_calories
            FROM users
            WHERE user_id = ?
            """,
            (
                user_id,
            )
        )
        row = await cursor.fetchone()
        return None if (row is None) else row[0]

async def get_today_calories(user_id):
    async with aiosqlite.connect("calorie_bot.db") as db:
        sm = await db.execute(
            """
            SELECT COALESCE(SUM(calories), 0)
            FROM food_entries
            WHERE user_id = ?
            AND DATE(created_at) = DATE('now')
            """,
            (
            user_id,
            )
        )
        row = await sm.fetchone()
        return row[0]
