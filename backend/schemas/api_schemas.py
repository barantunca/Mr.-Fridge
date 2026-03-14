from pydantic import BaseModel
from typing import List, Dict


# Envantere eşya eklerken mobil uygulamadan beklediğimiz veri
class ItemCreateRequest(BaseModel):
    house_id: int
    name: str
    category: str = "Diğer"


# Tarif üretmek için mobil uygulamadan beklediğimiz malzeme listesi
class RecipeGenerateRequest(BaseModel):
    ingredients: List[str]
