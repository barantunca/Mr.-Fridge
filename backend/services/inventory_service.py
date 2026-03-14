from sqlalchemy.orm import Session
from sqlalchemy import select
from models.item import Item
from typing import Dict, List


def add_item_to_inventory(
    db: Session, house_id: int, item_name: str, category: str = "Genel"
) -> Item:
    """
    Kameradan (Mr.Fridge vizyon servisinden) veya elle eklenen ürünü veritabanına kaydeder.
    Eşya isimleri 'Item' modelindeki @validates mantığı sayesinde otomatik olarak
    baş harfleri büyük ve boşluklardan arındırılmış (Set mantığı) şekilde kaydedilir.
    """
    new_item = Item(house_id=house_id, name=item_name, category=category)

    db.add(new_item)
    db.commit()
    db.refresh(new_item)  # Eklenen verinin ID'sini ve güncel halini döndürmek için

    return new_item


def get_categorized_inventory_for_recipe(
    db: Session, house_id: int
) -> Dict[str, List[str]]:
    """
    Yemek tarifi sekmesi için envanteri miktar gözetmeksizin,
    isim isim ve kategorize edilmiş biçimde frontend'e (uygulamaya) hazırlar.

    PERFORMANS ODAĞI:
    Tüm Item nesnelerini (tarihler, ID'ler vb.) RAM'e çekmek yerine,
    sadece 'category' ve 'name' sütunlarını 'distinct()' ile çekerek
    aynı isimdeki ürünlerin SQL seviyesinde tekilleştirilmesini sağlarız.
    """
    # SQLAlchemy 2.0 modern sorgu yapısı
    stmt = (
        select(Item.category, Item.name)
        .where(Item.house_id == house_id)
        .distinct()  # Aynı evde 5 tane "Süt" eklendiyse bile sadece 1 tane "Süt" getirir
        .order_by(Item.category, Item.name)
    )

    # db.execute ile sorguyu çalıştırıp sonuçları alıyoruz
    results = db.execute(stmt).all()

    # Frontend'in "kategorize biçimde önüne gelir" şartını sağlamak için sözlük (dict) oluşturuyoruz
    categorized_inventory = {}

    for category, name in results:
        # Kategori boş girilmişse güvenlik amaçlı varsayılan bir başlık atıyoruz
        cat_key = category if category else "Diğer"

        if cat_key not in categorized_inventory:
            categorized_inventory[cat_key] = []

        categorized_inventory[cat_key].append(name)

    return categorized_inventory


def delete_item_from_inventory(db: Session, item_id: int) -> bool:
    """
    Kullanıcının envanterden bir eşyayı silmesi gerektiğinde çalışacak fonksiyon.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False
