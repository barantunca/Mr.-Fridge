import os
from openai import OpenAI
from typing import List
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)


def generate_recipe_from_ingredients(selected_ingredients: List[str]) -> str:
    if not selected_ingredients:
        raise ValueError("Tarif üretebilmek için en az bir malzeme seçmelisiniz.")

    ingredients_str = ", ".join(selected_ingredients)

    prompt = (
        f"Elimde şu malzemeler var: {ingredients_str}. "
        "Bana sadece bu malzemeleri (ve mutfakta her zaman bulunabileceğini varsaydığımız tuz, karabiber, sıvı yağ, su gibi temel maddeleri) "
        "kullanarak yapabileceğim pratik ve lezzetli bir yemek tarifi ver. "
        "Lütfen önce yemeğin yaratıcı bir adını, ardından tahmini hazırlık süresini ve "
        "adım adım yapılışını anlaşılır bir Türkçe ile yaz."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Sen Mr.Fridge uygulaması içinde çalışan, pratik, yaratıcı ve israfı önleyen uzman bir şefsin.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(
            f"Yapay zeka tarifi hazırlarken bir sorunla karşılaştı: {str(e)}"
        )
