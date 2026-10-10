import asyncio

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from database import delete_old_food_entries

async def cleanup_old_entries() -> None:
    msk = datetime.now(ZoneInfo("Europe/Moscow"))
    start_today = msk.replace(hour=0, minute=0, second=0, microsecond=0)

    cutoff_msk = start_today - timedelta(days=6)
    cutoff_utc = cutoff_msk.astimezone(timezone.utc)

    await delete_old_food_entries(cutoff_utc.strftime("%Y-%m-%d %H:%M:%S"))

async def cleanup_scheduler() -> None:
    while True:
        await cleanup_old_entries()
        msk = datetime.now(ZoneInfo("Europe/Moscow"))
        next_night = msk.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        seconds = (next_night - msk).total_seconds()
        await asyncio.sleep(seconds)
