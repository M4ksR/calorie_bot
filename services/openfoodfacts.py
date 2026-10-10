import aiohttp

from config import MAIL

async def search_openfoodfacts(food_name, limit):
    async with aiohttp.ClientSession() as session:
        url = "https://world.openfoodfacts.org/cgi/search.pl"

        param = {
            "search_terms": food_name,
            "search_simple": 1,
            "action": "process",
            "page_size": limit,
            "json": 1,
            "fields": "code,product_name,brands,nutriments"
        }

        header = {"User-Agent": f"CalorieBot/1.0 {MAIL}"}

        async with session.get(url, params=param, headers=header) as response:
            if response.status == 200:
                data = await response.json()
                products = data.get('products', [])
                result = []
                for product in products:
                    nutriments = product.get('nutriments') or {}
                    food_params = {
                        "id": product.get('code'),
                        "name": product.get('product_name'),
                        "brand": product.get('brands'),
                        "calories": nutriments.get('energy-kcal-100g'),
                        "protein": nutriments.get('proteins_100g'),
                        "fat": nutriments.get('fat_100g'),
                        "carbs": nutriments.get('carbohydrates_100g'),
                        "source": "openfoodfacts",
                        "url": None
                    }
                    result.append(food_params)
                return result

    print("openfoodfacts API error")
    return []
