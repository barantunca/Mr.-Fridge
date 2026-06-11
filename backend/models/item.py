from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    # Changed from house_id to fridge_id, linked to fridges.id
    fridge_id = Column(
        Integer,
        ForeignKey("fridges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Item name (e.g. "Milk", "Apple")
    name = Column(String, nullable=False, index=True)

    # Item category (e.g. "Dairy", "Fruit")
    category = Column(String, nullable=True)

    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationship pointing to Fridge instead of House
    fridge = relationship("Fridge", back_populates="items")

    # --- SETTER LOGIC (Data Normalization) ---
    @validates("name")
    def validate_and_format_name(self, key, value):
        if not value:
            raise ValueError("Item name cannot be empty.")
        # Strip whitespace and title-case each word
        return " ".join(value.strip().split()).title()

    @validates("category")
    def validate_category(self, key, value):
        if value:
            return " ".join(value.strip().split()).title()
        return value

    # --- GETTER LOGIC (Custom Output) ---
    @property
    def display_info(self):
        if self.category:
            return f"[{self.category}] {self.name}"
        return self.name

    def __repr__(self):
        return f"<Item(name='{self.name}', category='{self.category}')>"
