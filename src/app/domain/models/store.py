import uuid

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    owner_id = Column(Uuid, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="store")
    products = relationship(
        "Product", back_populates="store", cascade="all, delete-orphan"
    )
    store_orders = relationship("StoreOrder", back_populates="store")
