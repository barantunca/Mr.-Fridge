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


@router.get("/{fridge_id}/items")
async def get_all_items(fridge_id: int, db: AsyncSession = Depends(get_db)):
    """
    Buzdolabındaki tüm eşyaları id, isim ve kategoriyle döner.
    Frontend'in silme işlemi için item id'lerine ihtiyacı var.
    """
    return await get_all_items_for_fridge(db=db, fridge_id=fridge_id)


@router.delete("/delete/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """
    Verilen id'ye sahip eşyayı veritabanından siler.
    """
    deleted = await delete_item_from_inventory(db=db, item_id=item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Eşya bulunamadı.")
    return {"status": "success", "message": f"Eşya (id={item_id}) silindi."}