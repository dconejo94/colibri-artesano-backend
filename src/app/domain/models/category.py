import uuid

from sqlalchemy import Column, String, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)

    from sqlalchemy import Index

    __table_args__ = (
        Index(
            "ix_categories_name_trgm",
            name,
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    products = relationship("Product", back_populates="category")
