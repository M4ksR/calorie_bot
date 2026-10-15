import aiohttp
import json

from config import GEMINI_API_KEY

async def estimate_foods(foods):
    async with aiohttp.ClientSession() as session:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }

        food_lines = []
        for food in foods:
            food_lines.append(f"{food['name']} - {food['weight']} г")

        products = "\n".join(food_lines)

        prompt = f'''
                Для каждого продукта укажи калории, белки, жиры и углеводы.
                Верни ровно по одному результату для каждого продукта.
                
                Сохраняй тот же порядок продуктов.
                Не пропускай элементы и не добавляй новые.
                КБЖУ должно быть рассчитано уже на указанный вес, а не на 100 г.
                Это приблизительная оценка, поэтому используй типичные средние значения продукта.

                {products}            
                '''

        body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "calories": {"type": "number"},
                            "protein": {"type": "number"},
                            "fat": {"type": "number"},
                            "carbs": {"type": "number"}
                        },
                        "required": [
                            "calories",
                            "protein",
                            "fat",
                            "carbs"
                        ]
                    }
                }
            }
        }

        async with session.post(url, headers=headers, json=body) as response:
            if response.status == 200:
                text = (await response.json())["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)

    print("gemini API error")
    return []
