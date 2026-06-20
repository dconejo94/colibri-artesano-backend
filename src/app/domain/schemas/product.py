from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from app.domain.schemas.product_image import ProductImageResponseDTO
from app.domain.schemas.product_variant import ProductVariantResponseDTO
from app.domain.schemas.store import StoreResponseDTO, StorePublicDTO
from app.domain.schemas.category import CategoryResponseDTO


class ProductCreateDTO(BaseModel):
    category_id: UUID
    name: str
    description: str | None = None
    base_price: Decimal
    is_active: bool = True


class ProductUpdateDTO(BaseModel):
    category_id: UUID | None = None
    name: str | None = None
    description: str | None = None
    base_price: Decimal | None = None
    is_active: bool | None = None


class ProductListDTO(BaseModel):
    """Lean projection used in paginated list endpoints.

    Deliberately omits ``owner_id`` (exposed inside the store object) and
    ``variants`` to keep mobile payloads small.  ``store`` is included as a
    minimal reference (name + id) so the UI can display it without a second
    request; ``owner_id`` is excluded from the store sub-object below.
    """

    id: UUID
    store_id: UUID
    category_id: UUID | None
    name: str
    description: str | None
    base_price: Decimal
    stock: int
    is_active: bool
    created_at: datetime

    # Public store reference — omits owner_id deliberately.
    store: StorePublicDTO | None = None
    category: CategoryResponseDTO | None = None
    images: list[ProductImageResponseDTO] = []

    model_config = {"from_attributes": True}


class ProductResponseDTO(BaseModel):
    """Full product projection — used internally and for write-operation
    responses (create/update).  Kept for backwards compatibility with
    existing callers that depend on the full shape."""

    id: UUID
    store_id: UUID
    category_id: UUID | None
    name: str
    description: str | None
    base_price: Decimal
    stock: int
    is_active: bool
    created_at: datetime

    store: StoreResponseDTO | None = None
    category: CategoryResponseDTO | None = None
    images: list[ProductImageResponseDTO] = []
    variants: list[ProductVariantResponseDTO] = []

    model_config = {"from_attributes": True}


class ProductDetailResponseDTO(ProductResponseDTO):
    """Rich projection for GET /products/{id}.

    Inherits the full structure of ``ProductResponseDTO`` and is the
    intended response type for the detail endpoint.  Separated from the
    base class so that the detail endpoint can be independently evolved
    (e.g. add review counts, related products) without touching the list DTO.

    # PERF-NOTE: create_product / update_product fire an extra
    # get_product_by_id round-trip to populate relations (avoiding the
    # MissingGreenlet error from lazy-loading outside an async context).
    # This is the correct approach; optimize later by eager-loading inside
    # the repository's create/update queries if latency becomes a concern.
    """

    pass
