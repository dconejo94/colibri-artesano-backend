from sqlalchemy import Column, DateTime, Uuid, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProductFavorite(Base):
    __tablename__ = "product_favorites"

    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(
        Uuid, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="favorite_products")
    product = relationship("Product", back_populates="favorited_by")
