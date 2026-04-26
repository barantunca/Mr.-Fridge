from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    # house_id yerine fridge_id yapıldı ve fridges.id'ye bağlandı
    fridge_id = Column(
        Integer,
        ForeignKey("fridges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Eşyanın adı ("Süt", "Elma" vb.)
    name = Column(String, nullable=False, index=True)

    # Eşyanın kategorisi ("Süt Ürünleri", "Meyve" vb.)
    category = Column(String, nullable=True)

    added_at = Column(DateTime, default=datetime.utcnow)

    # İlişki House yerine Fridge'e yönlendirildi
    fridge = relationship("Fridge", back_populates="items")

    # --- SETTER MANTIĞI (Veri Temizleme) ---
    @validates("name")
    def validate_and_format_name(self, key, value):
        if not value:
            raise ValueError("Eşya adı boş olamaz.")
        # Boşlukları temizle ve her kelimenin ilk harfini büyüt (Title Case)
        return " ".join(value.strip().split()).title()

    @validates("category")
    def validate_category(self, key, value):
        if value:
            return " ".join(value.strip().split()).title()
        return value

    # --- GETTER MANTIĞI (Özelleştirilmiş Çıktı) ---
    @property
    def display_info(self):
        if self.category:
            return f"[{self.category}] {self.name}"
        return self.name

    def __repr__(self):
        return f"<Item(name='{self.name}', category='{self.category}')>"
