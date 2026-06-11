from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.item import Item
from typing import Dict, List
import time

# Simple in-memory cache (for performance)
_inventory_cache = {}
CACHE_TTL = 60  # Cache lifetime in seconds

async def add_item_to_inventory(
    db: AsyncSession, fridge_id: int, item_name: str, category: str = "Other"
) -> Item:
    new_item = Item(fridge_id=fridge_id, name=item_name, category=category)

    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    # Invalidate the cache when a new item is added so the list stays fresh
    if fridge_id in _inventory_cache:
        del _inventory_cache[fridge_id]

    return new_item

async def get_categorized_inventory_for_recipe(
    db: AsyncSession, fridge_id: int
) -> Dict[str, List[str]]:
    
    current_time = time.time()
    # Cache check
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
        cat_key = category if category else "Other"
        if cat_key not in categorized_inventory:
            categorized_inventory[cat_key] = []
        categorized_inventory[cat_key].append(name)

    # Store the result in cache
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
    """Returns all items in the fridge with id, name, and category."""
    stmt = (
        select(Item.id, Item.name, Item.category)
        .where(Item.fridge_id == fridge_id)
        .order_by(Item.category, Item.name)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [{"id": r.id, "name": r.name, "category": r.category or "Other"} for r in rows]