from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, List

# Kendi yazdığımız servisler ve şemalar
from schemas.api_schemas import ItemCreateRequest
from services.inventory_service import (
    add_item_to_inventory,
    get_categorized_inventory_for_recipe,
)
from core.database import (
    get_db,
)  # Veritabanı bağlantısı için (henüz yazmadık ama bağlanacak)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/add")
async def add_item(request: ItemCreateRequest, db: Session = Depends(get_db)):
    """
    Mobil uygulamadan gelen eşyayı veritabanına kaydeder.
    """
    # Try-catch yok! Hata olursa exception_handler yakalayacak.
    new_item = add_item_to_inventory(
        db=db,
        house_id=request.house_id,
        item_name=request.name,
        category=request.category,
    )
    return {"status": "success", "message": f"{new_item.name} envantere eklendi."}


@router.get("/{house_id}/categorized", response_model=Dict[str, List[str]])
async def get_categorized_inventory(house_id: int, db: Session = Depends(get_db)):
    """
    Yemek tarifi sekmesi açıldığında çalışır.
    Miktar gözetmeksizin, isim isim ve kategorize edilmiş listeyi döner.
    """
    # Doğrudan servisi çağır ve veriyi dön
    return get_categorized_inventory_for_recipe(db=db, house_id=house_id)
