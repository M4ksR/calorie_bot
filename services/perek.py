import aiohttp

from config import PEREK_API_KEY

async def search_perek(food_name, limit):
    async with aiohttp.ClientSession() as session:
        url = "https://perek.us/api/v1/foods/search"

        param = {
            "q": food_name,
            "limit": limit,
            "market": "ru"
        }

        header = {"X-API-KEY": PEREK_API_KEY}

        async with session.get(url, params=param, headers=header) as response:
            if response.status == 200:
                data = await response.json()
                foods = data.get('foods', [])
                result = []
                for food in foods:
                    per100 = food.get('per100') or {}
                    brand = food.get('brand') or {}
                    food_params = {
                        "id": food.get('id'),
                        "name": food.get('name'),
                        "brand": brand.get('name'),
                        "calories": per100.get('kcal'),
                        "protein": per100.get('protein'),
                        "fat": per100.get('fat'),
                        "carbs": per100.get('carbs'),
                        "source": "perek",
                        "url": food.get('url')
                    }
                    result.append(food_params)
                return result

    print("perek API error")
    return []
