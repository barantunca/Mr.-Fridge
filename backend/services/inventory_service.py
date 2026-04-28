from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.item import Item
from typing import Dict, List
from datetime import datetime
import time

def get_lifespan_for_category(category_name: str) -> int:
    if not category_name:
        return 14
        
    cat = category_name.lower()
    if "süt" in cat or "peynir" in cat or "yoğurt" in cat or "kaymak" in cat:
        return 7
    elif "et" in cat or "tavuk" in cat or "balık" in cat or "kıyma" in cat or "sucuk" in cat or "salam" in cat:
        return 5
    elif "sebze" in cat or "yeşillik" in cat or "mantar" in cat:
        return 10
    elif "meyve" in cat:
        return 14
    elif "bakliyat" in cat or "kuru" in cat or "tahıl" in cat:
        return 180
    elif "kahvaltılık" in cat or "sos" in cat or "salça" in cat:
        return 90
    elif "içecek" in cat or "su" in cat:
        return 30
    elif "hamur" in cat or "tatlı" in cat or "ekmek" in cat:
        return 5
    
    return 14

def guess_category_from_name(name: str) -> str:
    if not name:
        return "Diğer"
        
    n = name.lower()
    if any(k in n for k in ["süt", "peynir", "yoğurt", "kefir", "tereyağ", "ayran", "kaymak", "krem", "çökelek", "lor", "labne", "kaşar", "tulum", "hellim", "mozzarella"]):
        return "Süt Ürünleri"
    elif any(k in n for k in ["et", "tavuk", "balık", "kıyma", "sucuk", "sosis", "pastırma", "salam", "kavurma", "köfte", "ciğer", "bonfile", "antrikot", "hindi", "jambon"]):
        return "Et Ürünleri"
    elif any(k in n for k in ["domates", "biber", "patlıcan", "kabak", "salatalık", "havuç", "soğan", "sarımsak", "marul", "maydanoz", "ıspanak", "brokoli", "lahana", "sebze", "nane", "dereotu", "roka", "tere", "pırasa", "karnabahar", "enginar", "kereviz", "bezelye", "taze fasulye", "bamya", "turp", "mantar"]):
        return "Sebzeler"
    elif any(k in n for k in ["elma", "armut", "muz", "çilek", "karpuz", "kavun", "üzüm", "şeftali", "kiraz", "erik", "portakal", "mandalina", "limon", "meyve", "nar", "incir", "kivi", "vişne", "dut", "ayva", "greyfurt", "böğürtlen"]):
        return "Meyveler"
    elif any(k in n for k in ["mercimek", "nohut", "fasulye", "pirinç", "bulgur", "makarna", "un", "şeker", "yulaf", "arpa", "buğday", "tarhana", "kuskus", "irmik", "mısır"]):
        return "Bakliyatlar"
    elif any(k in n for k in ["su", "kola", "meyve suyu", "soda", "gazoz", "şalgam", "limonata", "soğuk çay", "bira", "şarap", "içecek"]):
        return "İçecekler"
    elif any(k in n for k in ["zeytin", "reçel", "bal", "pekmez", "tahin", "salça", "ketçap", "mayonez", "hardal", "sos", "nar ekşisi", "sirke", "marmelat"]):
        return "Kahvaltılık & Sos"
    elif any(k in n for k in ["ekmek", "pide", "lavaş", "yufka", "simit", "poğaça", "açma", "börek", "baklava", "kadayıf", "sütlaç", "puding", "pasta", "kek", "kurabiye", "tatlı", "hamur"]):
        return "Hamur İşi & Tatlı"
        
    return "Diğer"

# Basit bir In-Memory Önbellek (Performans için)
_inventory_cache = {}
CACHE_TTL = 60 # Saniye cinsinden cache süresi

async def add_item_to_inventory(
    db: AsyncSession, fridge_id: int, item_name: str, category: str = "Genel"
) -> Item:
    # Kullanıcı kategoriyi boş bıraktıysa akıllı tahmin yap
    if not category or category.strip().lower() in ["", "genel", "diğer", "null", "none"]:
        final_category = guess_category_from_name(item_name)
    else:
        final_category = category.strip()
        
    new_item = Item(fridge_id=fridge_id, name=item_name, category=final_category)

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
    item = result.scalars().first()
    
    if item:
        # Cache'i temizle
        fridge_id = item.fridge_id
        if fridge_id in _inventory_cache:
            del _inventory_cache[fridge_id]

        await db.delete(item)
        await db.commit()
        return True
    return False


async def get_all_items_for_fridge(db: AsyncSession, fridge_id: int):
    """Buzdolabındaki tüm eşyaları id, name, category ve days_left ile döner."""
    stmt = (
        select(Item.id, Item.name, Item.category, Item.added_at)
        .where(Item.fridge_id == fridge_id)
        .order_by(Item.added_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    now = datetime.utcnow()
    items_out = []
    
    for r in rows:
        cat = r.category or "Diğer"
        lifespan = get_lifespan_for_category(cat)
        
        # Calculate days elapsed since added_at
        # Handle cases where added_at might be None (old data)
        added_date = r.added_at or now
        delta_days = (now - added_date).days
        days_left = lifespan - delta_days
        
        items_out.append({
            "id": r.id, 
            "name": r.name, 
            "category": cat,
            "days_left": days_left
        })
        
    return items_out