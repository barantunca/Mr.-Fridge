from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from schemas.api_schemas import ItemCreateRequest
from services.inventory_service import (
    add_item_to_inventory,
    get_categorized_inventory_for_recipe,
)
from core.database import get_db

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.post("/add")
async def add_item(request: ItemCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Mobil uygulamadan gelen eşyayı veritabanına kaydeder.
    """
    new_item = await add_item_to_inventory(
        db=db,
        fridge_id=request.fridge_id,
        item_name=request.name,
        category=request.category,
    )
    return {"status": "success", "message": f"{new_item.name} envantere eklendi."}

@router.get("/{fridge_id}/categorized", response_model=Dict[str, List[str]])
async def get_categorized_inventory(fridge_id: int, db: AsyncSession = Depends(get_db)):
    """
    Yemek tarifi sekmesi açıldığında çalışır (Önbelleklidir).
    """
    return await get_categorized_inventory_for_recipe(db=db, fridge_id=fridge_id)