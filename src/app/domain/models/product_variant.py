import uuid

from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    product_id = Column(
        Uuid, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    price_modifier = Column(Numeric(10, 2), default=0)
    stock_quantity = Column(Integer, default=0)

    product = relationship("Product", back_populates="variants")
    images = relationship(
        "ProductImage",
        back_populates="variant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
