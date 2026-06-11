from pydantic import BaseModel
from typing import List


# Data expected from the mobile app when adding an item to the inventory
class ItemCreateRequest(BaseModel):
    fridge_id: int  # Changed from house_id to fridge_id
    name: str
    category: str = "Other"


# Ingredient list expected from the mobile app for recipe generation
class RecipeGenerateRequest(BaseModel):
    ingredients: List[str]
