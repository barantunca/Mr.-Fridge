from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.item import Item
from typing import Dict, List
import time

# Basit bir In-Memory Önbellek (Performans için)
_inventory_cache = {}
CACHE_TTL = 60 # Saniye cinsinden cache süresi

async def add_item_to_inventory(
    db: AsyncSession, fridge_id: int, item_name: str, category: str = "Genel"
) -> Item:
    new_item = Item(fridge_id=fridge_id, name=item_name, category=category)

    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    # Yeni eşya eklendiğinde cache'i temizle ki liste güncellensin
    if fridge_id in _inventory_cache:
        del _inventory_cache[fridge_id]

    return new_item

async def get_categorized_inventory_for_recipe(
    db: AsyncSession, fridge_id: int
) -> Dict[str, List[str]]:
    
    current_time = time.time()
    # Cache kontrolü
    if fridge_id in _inventory_cache:
        cache_data, timestamp = _inventory_cache[fridge_id]
        if current_time - timestamp < CACHE_TTL:
            return cache_data

    stmt = (
        select(Item.category, Item.name)
        .where(Item.fridge_id == fridge_id)
        .distinct()
        .order_by(Item.category, Item.name)
    )

    result = await db.execute(stmt)
    results = result.all()
    
    categorized_inventory = {}

    for category, name in results:
        cat_key = category if category else "Diğer"
        if cat_key not in categorized_inventory:
            categorized_inventory[cat_key] = []
        categorized_inventory[cat_key].append(name)

    # Sonucu önbelleğe al
    _inventory_cache[fridge_id] = (categorized_inventory, current_time)

    return categorized_inventory

async def delete_item_from_inventory(db: AsyncSession, item_id: int) -> bool:
    stmt = select(Item).filter(Item.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_first()
    
    if item:
        await db.delete(item)
        await db.commit()
        return True
    return False


async def get_all_items_for_fridge(db: AsyncSession, fridge_id: int):
    """Buzdolabındaki tüm eşyaları id, name, category ile döner."""
    stmt = (
        select(Item.id, Item.name, Item.category)
        .where(Item.fridge_id == fridge_id)
        .order_by(Item.category, Item.name)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [{"id": r.id, "name": r.name, "category": r.category or "Diğer"} for r in rows]