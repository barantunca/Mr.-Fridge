from pydantic import BaseModel
from typing import List


# Envantere eşya eklerken mobil uygulamadan beklediğimiz veri
class ItemCreateRequest(BaseModel):
    fridge_id: int  # house_id yerine fridge_id oldu
    name: str
    category: str = "Diğer"


# Tarif üretmek için mobil uygulamadan beklediğimiz malzeme listesi
class RecipeGenerateRequest(BaseModel):
    ingredients: List[str]
