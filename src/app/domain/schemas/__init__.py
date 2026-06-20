from app.domain.schemas.paginated_response import PaginatedResponse as PaginatedResponse
from app.domain.schemas.category import CategoryResponseDTO as CategoryResponseDTO
from app.domain.schemas.store import StorePublicDTO as StorePublicDTO
from app.domain.schemas.store import StoreResponseDTO as StoreResponseDTO
from app.domain.schemas.product import ProductListDTO as ProductListDTO
from app.domain.schemas.product import ProductResponseDTO as ProductResponseDTO
from app.domain.schemas.product import (
    ProductDetailResponseDTO as ProductDetailResponseDTO,
)
from app.domain.schemas.product_image import (
    ProductImageResponseDTO as ProductImageResponseDTO,
)
from app.domain.schemas.product_variant import (
    ProductVariantResponseDTO as ProductVariantResponseDTO,
)
from app.domain.schemas.order import MainOrderResponseDTO as MainOrderResponseDTO
from app.domain.schemas.order import StoreOrderResponseDTO as StoreOrderResponseDTO
from app.domain.schemas.search import ProductAutocompleteDTO as ProductAutocompleteDTO
from app.domain.schemas.notification import (
    FCMTokenDTO as FCMTokenDTO,
    NotificationResponseDTO as NotificationResponseDTO,
    NotificationListResponseDTO as NotificationListResponseDTO
)