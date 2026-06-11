from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from schemas.api_schemas import ItemCreateRequest
from services.inventory_service import (
    add_item_to_inventory,
    get_categorized_inventory_for_recipe,
    delete_item_from_inventory,
    get_all_items_for_fridge,
)
from core.database import get_db

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/add")
async def add_item(request: ItemCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Receives an item from the mobile app and saves it to the database.
    """
    new_item = await add_item_to_inventory(
        db=db,
        fridge_id=request.fridge_id,
        item_name=request.name,
        category=request.category,
    )
    return {"status": "success", "message": f"{new_item.name} has been added to the inventory."}


@router.get("/{fridge_id}/categorized", response_model=Dict[str, List[str]])
async def get_categorized_inventory(fridge_id: int, db: AsyncSession = Depends(get_db)):
    """
    Called when the recipe tab is opened (cached).
    """
    return await get_categorized_inventory_for_recipe(db=db, fridge_id=fridge_id)


@router.get("/{fridge_id}/items")
async def get_all_items(fridge_id: int, db: AsyncSession = Depends(get_db)):
    """
    Returns all items in the fridge with their id, name, and category.
    The frontend needs item IDs for deletion operations.
    """
    return await get_all_items_for_fridge(db=db, fridge_id=fridge_id)


@router.delete("/delete/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """
    Deletes the item with the given ID from the database.
    """
    deleted = await delete_item_from_inventory(db=db, item_id=item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found.")
    return {"status": "success", "message": f"Item (id={item_id}) has been deleted."}