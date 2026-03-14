from sqlalchemy.orm import Session
from sqlalchemy import select
from models.item import Item
from typing import Dict, List


def add_item_to_inventory(
    db: Session, fridge_id: int, item_name: str, category: str = "Genel"
) -> Item:
    new_item = Item(fridge_id=fridge_id, name=item_name, category=category)

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


def get_categorized_inventory_for_recipe(
    db: Session, fridge_id: int
) -> Dict[str, List[str]]:
    stmt = (
        select(Item.category, Item.name)
        .where(Item.fridge_id == fridge_id)
        .distinct()
        .order_by(Item.category, Item.name)
    )

    results = db.execute(stmt).all()
    categorized_inventory = {}

    for category, name in results:
        cat_key = category if category else "Diğer"
        if cat_key not in categorized_inventory:
            categorized_inventory[cat_key] = []
        categorized_inventory[cat_key].append(name)

    return categorized_inventory


def delete_item_from_inventory(db: Session, item_id: int) -> bool:
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False
