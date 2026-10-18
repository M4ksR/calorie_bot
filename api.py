from fastapi import FastAPI, Header, HTTPException, Depends, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import (get_dashboard_data,
                      get_weekly_calories,
                      get_today_food_entries,
                      delete_food_entry,
                      get_saved_food,
                      get_saved_food_by_id,
                      add_food_and_update_streak)
from services.telegram_auth import validate_init_data

app = FastAPI()
app.mount("/static", StaticFiles(directory="web"), name="static")

async def get_current_user_id(init_data: str | None = Header(default=None, alias="X-Telegram-Init-Data")):
    if not init_data: raise HTTPException(status_code=401, detail="Invalid Telegram initData")

    user_id = validate_init_data(init_data)
    if user_id is None: raise HTTPException(status_code=401, detail="Invalid Telegram initData")

    return user_id

@app.get("/")
async def mini_app():
    return FileResponse("web/index.html")

@app.get("/api/me")
async def me(user_id: int = Depends(get_current_user_id)):
    return {"user_id": user_id}

@app.get("/api/dashboard")
async def dashboard(user_id: int = Depends(get_current_user_id)):
    return await get_dashboard_data(user_id)

@app.get("/api/weekly")
async def weekly(user_id: int = Depends(get_current_user_id)):
    return await get_weekly_calories(user_id)

@app.get("/api/today-foods")
async def today_foods(user_id: int = Depends(get_current_user_id)):
    entries = await get_today_food_entries(user_id)
    result = []

    for entry in entries:
        result.append({
            "id": entry[0],
            "name": entry[1],
            "weight": entry[2],
            "calories": entry[3]
        })

    return result

@app.delete("/api/today-foods/{entry_id}")
async def delete_today_food(entry_id: int, user_id: int = Depends(get_current_user_id)):
    await delete_food_entry(entry_id, user_id)
    return {"ok": True}

@app.get("/api/saved-foods")
async def saved_foods(user_id: int = Depends(get_current_user_id)):
    foods = await get_saved_food(user_id)
    result = []

    for food in foods:
        result.append({
            "id": food[0],
            "name": food[1],
            "calories": food[2],
            "protein": food[3],
            "fat": food[4],
            "carbs": food[5]
        })

    return result

@app.post("/api/saved-foods/{food_id}/add")
async def add_saved_food(food_id: int,
                         weight: float = Body(embed=True),
                         user_id: int = Depends(get_current_user_id)):
    if weight <= 0: raise HTTPException(status_code=400, detail="Invalid weight")

    food = await get_saved_food_by_id(food_id, user_id)
    if food is None: raise HTTPException(status_code=404, detail="Saved food not found")

    coef = weight / 100
    await add_food_and_update_streak(user_id,
                                     food[0],
                                     weight,
                                     food[1] * coef,
                                     food[2] * coef,
                                     food[3] * coef,
                                     food[4] * coef)

    return {"ok": True}
