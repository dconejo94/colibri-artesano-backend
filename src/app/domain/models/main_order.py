import uuid

from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class MainOrder(Base):
    __tablename__ = "main_orders"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    buyer_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    buyer = relationship("User", back_populates="orders")
    store_orders = relationship(
        "StoreOrder",
        back_populates="main_order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
