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
