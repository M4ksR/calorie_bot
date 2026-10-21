from fastapi import FastAPI, Header, HTTPException, Depends, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import (get_dashboard_data,
                      get_weekly_calories,
                      get_today_food_entries,
                      delete_food_entry,
                      get_saved_food,
                      get_saved_food_by_id,
                      add_food_and_update_streak,
                      search_products)
from services.perek import search_perek
from services.gemini import estimate_foods
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

@app.get("/api/products")
async def products(query: str, page: int = 0, user_id: int = Depends(get_current_user_id)):
    page_size = 10
    if page < 0: page = 0

    result, total = await search_products(query, page, page_size)

    if total > 0:
        return {
            "products": result,
            "total": total,
            "page": page,
            "page_size": page_size,
            "source": "local"
        }

    if page > 0:
        return {
            "products": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "source": "perek"
        }

    perek_products = await search_perek(query, 10)
    result = []

    for product in perek_products:
        result.append({
            "id": None,
            "source": "perek",
            "name": product.get("name", ""),
            "brand": product.get("brand"),
            "calories": product.get("calories", 0),
            "protein": product.get("protein", 0),
            "fat": product.get("fat", 0),
            "carbs": product.get("carbs", 0),
            "weight": product.get("weight"),
            "weight_unit": product.get("weight_unit"),
            "url": product.get("url"),
            "image_url": product.get("image_url")
        })

    return {
        "products": result,
        "total": len(result),
        "page": 0,
        "page_size": page_size,
        "source": "perek"
    }

@app.post("/api/products/add")
async def add_product(data: dict = Body(...),
                      user_id: int = Depends(get_current_user_id)):
    try:
        name = str(data["name"]).strip()
        weight = float(data["weight"])
        calories = float(data["calories"])
        protein = float(data["protein"])
        fat = float(data["fat"])
        carbs = float(data["carbs"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid product")

    if not name or weight <= 0: raise HTTPException(status_code=400, detail="Invalid product")

    coef = weight / 100
    await add_food_and_update_streak(user_id,
                                     name,
                                     weight,
                                     calories * coef,
                                     protein * coef,
                                     fat * coef,
                                     carbs * coef)

    return {"ok": True}

@app.post("/api/manual-food")
async def add_manual_food(data: dict = Body(...),
                          user_id: int = Depends(get_current_user_id)):
    try:
        name = str(data["name"]).strip()
        weight = float(data["weight"])
        calories = float(data["calories"])
        protein = float(data["protein"])
        fat = float(data["fat"])
        carbs = float(data["carbs"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid food")

    if not name or weight <= 0: raise HTTPException(status_code=400, detail="Invalid food")

    coef = weight / 100
    await add_food_and_update_streak(user_id,
                                     name,
                                     weight,
                                     calories * coef,
                                     protein * coef,
                                     fat * coef,
                                     carbs * coef)

    return {"ok": True}

@app.post("/api/ai-food/estimate")
async def estimate_ai_food(data: dict = Body(...),
                           user_id: int = Depends(get_current_user_id)):
    foods = data.get("foods", [])
    if not foods: raise HTTPException(status_code=400, detail="No foods")

    prepared_foods = []
    for food in foods:
        try:
            name = str(food["name"]).strip()
            weight = float(food["weight"])
        except (KeyError, TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid food")

        if not name or weight <= 0: raise HTTPException(status_code=400, detail="Invalid food")
        prepared_foods.append({"name": name, "weight": weight})

    result = await estimate_foods(prepared_foods)
    if not result or len(result) != len(prepared_foods):
        raise HTTPException(status_code=503, detail="Gemini unavailable")

    estimated_foods = []
    for i, food in enumerate(prepared_foods):
        estimated_foods.append({
            "name": food["name"],
            "weight": food["weight"],
            "calories": result[i]["calories"],
            "protein": result[i]["protein"],
            "fat": result[i]["fat"],
            "carbs": result[i]["carbs"]
        })

    return estimated_foods

@app.post("/api/ai-food/add")
async def add_ai_food(data: dict = Body(...),
                      user_id: int = Depends(get_current_user_id)):
    foods = data.get("foods", [])
    if not foods: raise HTTPException(status_code=400, detail="No foods")

    for food in foods:
        try:
            name = str(food["name"]).strip()
            weight = float(food["weight"])
            calories = float(food["calories"])
            protein = float(food["protein"])
            fat = float(food["fat"])
            carbs = float(food["carbs"])
        except (KeyError, TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid food")

        if not name or weight <= 0: raise HTTPException(status_code=400, detail="Invalid food")

        await add_food_and_update_streak(user_id,
                                         name,
                                         weight,
                                         calories,
                                         protein,
                                         fat,
                                         carbs)

    return {"ok": True}
