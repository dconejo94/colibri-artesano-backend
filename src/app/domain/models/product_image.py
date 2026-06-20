import uuid

from sqlalchemy import Column, String, Boolean, ForeignKey, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    variant_id = Column(
        Uuid,
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
    )
    image_url = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)

    variant = relationship("ProductVariant", back_populates="images")
