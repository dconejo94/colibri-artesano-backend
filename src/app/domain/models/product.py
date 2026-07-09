import uuid

from sqlalchemy import (
    Column,
    String,
    Boolean,
    Numeric,
    ForeignKey,
    DateTime,
    Text,
    Uuid,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    store_id = Column(Uuid, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(
        Uuid, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index(
            "ix_products_name_trgm",
            name,
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
        Index(
            "ix_products_description_trgm",
            description,
            postgresql_using="gin",
            postgresql_ops={"description": "gin_trgm_ops"},
        ),
    )

    store = relationship("Store", back_populates="products")
    category = relationship("Category", back_populates="products")
    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    favorited_by = relationship(
        "ProductFavorite", back_populates="product", cascade="all, delete-orphan"
    )

    @property
    def stock(self) -> int:
        """Total available stock, derived from the variants.

        The variant is the single source of truth for stock; the product-level
        figure is just their sum (never stored, so it cannot drift). Callers
        must eager-load ``variants`` before reading this.
        """
        return sum(variant.stock_quantity or 0 for variant in self.variants)
