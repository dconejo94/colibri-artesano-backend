import uuid

from sqlalchemy import Column, Integer, Numeric, ForeignKey, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    store_order_id = Column(
        Uuid, ForeignKey("store_orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id = Column(Uuid, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Uuid, ForeignKey("product_variants.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    store_order = relationship("StoreOrder", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")
