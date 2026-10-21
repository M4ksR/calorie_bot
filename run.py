import asyncio
import logging
import os
import shutil
import sys

from pathlib import Path

import uvicorn

def prepare_runtime_database():
    runtime_path = os.getenv("RUNTIME_DB_PATH")
    if not runtime_path: return

    runtime_db = Path(runtime_path)
    runtime_db.parent.mkdir(parents=True, exist_ok=True)

    local_db = Path("calorie_bot.db")

    if not runtime_db.exists():
        if local_db.exists() and not local_db.is_symlink():
            shutil.copy2(local_db, runtime_db)
        else:
            runtime_db.touch()

    if local_db.is_symlink():
        local_db.unlink()
    elif local_db.exists():
        local_db.unlink()

    local_db.symlink_to(runtime_db)

async def start_api():
    port = int(os.getenv("PORT", "8000"))
    config = uvicorn.Config("api:app",
                            host="0.0.0.0",
                            port=port,
                            log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def start():
    prepare_runtime_database()

    from main import main as bot_main

    await asyncio.gather(
        bot_main(),
        start_api()
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(start())
