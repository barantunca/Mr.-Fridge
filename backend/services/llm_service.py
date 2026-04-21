import os
from openai import AsyncOpenAI
from typing import List
from core.api_key_store import get_api_key

# Lazy init: api_key_store'dan her zaman güncel key alınır
_client = None
def _get_client() -> AsyncOpenAI:
    global _client
    api_key = get_api_key()
    if not api_key:
        raise ValueError(
            "OpenAI API key eksik. Profil > Hesap Ayarları bölümünden "
            "API key'inizi girin."
        )
    if _client is None:
        _client = AsyncOpenAI(api_key=api_key)
    return _client

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
        response = await _get_client().chat.completions.create(
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