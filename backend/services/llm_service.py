import os
from openai import AsyncOpenAI
from typing import List
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=API_KEY)

async def generate_recipe_stream(selected_ingredients: List[str]):
    """Yemek tarifini asenkron olarak ve parça parça (chunk) üretir."""
    if not selected_ingredients:
        yield "Tarif üretebilmek için en az bir malzeme seçmelisiniz."
        return

    ingredients_str = ", ".join(selected_ingredients)

    prompt = (
        f"Elimde şu malzemeler var: {ingredients_str}. "
        "Bana sadece bu malzemeleri (ve mutfakta her zaman bulunabileceğini varsaydığımız tuz, karabiber, sıvı yağ, su gibi temel maddeleri) "
        "kullanarak yapabileceğim pratik ve lezzetli bir yemek tarifi ver. "
        "Lütfen önce yemeğin yaratıcı bir adını, ardından tahmini hazırlık süresini ve "
        "adım adım yapılışını anlaşılır bir Türkçe ile yaz."
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sen Mr.Fridge uygulaması içinde çalışan, pratik, yaratıcı ve israfı önleyen uzman bir şefsin."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.7,
            stream=True  # Akış modunu açtık
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    except Exception as e:
        yield f"\n[Hata oluştu: {str(e)}]"