from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    # Performans: house_id üzerinden çok sık filtreleme yapılacağı için indeksliyoruz.
    house_id = Column(
        Integer, ForeignKey("houses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Eşyanın adı ("Süt", "Elma" vb.)
    name = Column(String, nullable=False, index=True)

    # Eşyanın kategorisi ("Süt Ürünleri", "Meyve" vb.) - Tarif sekmesinde gruplama için kullanılacak
    category = Column(String, nullable=True)

    added_at = Column(DateTime, default=datetime.utcnow)

    # İlişki tanımlaması
    house = relationship("House", back_populates="items")

    # --- SETTER MANTIĞI (Veri Temizleme) ---
    @validates("name")
    def validate_and_format_name(self, key, value):
        """
        Kameradan dönen veya elle girilen eşya adını veritabanına kaydetmeden önce
        gereksiz boşluklardan arındırır ve ilk harflerini büyütür.
        Böylece " süt ", "yarım ELMA" gibi girdiler standart olarak "Süt", "Yarım Elma" olur.
        Türkçe dil yapısına uygun ve temiz bir envanter listesi sağlar.
        """
        if not value:
            raise ValueError("Eşya adı boş olamaz.")

        # Boşlukları temizle ve her kelimenin ilk harfini büyüt (Title Case)
        clean_name = " ".join(value.strip().split()).title()
        return clean_name

    @validates("category")
    def validate_category(self, key, value):
        if value:
            return " ".join(value.strip().split()).title()
        return value

    # --- GETTER MANTIĞI (Özelleştirilmiş Çıktı) ---
    @property
    def display_info(self):
        """
        Uygulama arayüzünde (veya tarif üretme sekmesinde) eşyaları listelerken
        kullanılabilecek hazır formatlanmış bir özellik (property) döndürür.
        """
        if self.category:
            return f"[{self.category}] {self.name}"
        return self.name

    def __repr__(self):
        return f"<Item(name='{self.name}', category='{self.category}')>"
