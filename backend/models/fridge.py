from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# Import Base from the application's core/database module
from core.database import Base


class Fridge(Base):
    __tablename__ = "fridges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Performance: lazy="selectin" fetches fridge items in a single SQL query,
    # avoiding the N+1 query problem.
    items = relationship(
        "Item", back_populates="fridge", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self):
        return f"<Fridge(name='{self.name}')>"
