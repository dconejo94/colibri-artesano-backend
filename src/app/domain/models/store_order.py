import uuid

from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class StoreOrder(Base):
    __tablename__ = "store_orders"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    main_order_id = Column(
        Uuid, ForeignKey("main_orders.id", ondelete="CASCADE"), nullable=False
    )
    store_id = Column(Uuid, ForeignKey("stores.id"), nullable=False)
    seller_status = Column(String, default="pending")
    subtotal_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    main_order = relationship("MainOrder", back_populates="store_orders")
    store = relationship("Store", back_populates="store_orders")
    items = relationship(
        "OrderItem",
        back_populates="store_order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
