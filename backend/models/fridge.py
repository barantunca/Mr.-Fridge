from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# Base sınıfını uygulamanın core veya db dosyasından import ettiğini varsayıyoruz
from core.database import Base


class Fridge(Base):
    __tablename__ = "fridges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Performans: lazy="selectin" ile evin içindeki eşyalar tek bir SQL sorgusuyla hızlıca çekilir.
    # N+1 sorgu problemini engeller.
    items = relationship(
        "Item", back_populates="fridge", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self):
        return f"<Fridge(name='{self.name}')>"
