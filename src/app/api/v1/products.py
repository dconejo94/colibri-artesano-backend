from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.services.product_service import ProductService
from app.services.product_image_service import ProductImageService
from app.services.product_variant_service import ProductVariantService
from app.api.deps import (
    get_product_service,
    get_product_image_service,
    get_product_variant_service,
    get_blob_storage_service,
)
from app.domain.schemas.product import (
    ProductUpdateDTO,
    ProductListDTO,
    ProductResponseDTO,
    ProductDetailResponseDTO,
)
from app.domain.schemas.product_image import (
    ProductImageCreateDTO,
    ProductImageResponseDTO,
    ProductImageUploadRequestDTO,
    ProductImageUploadResponseDTO,
)
from app.domain.schemas.product_variant import (
    ProductVariantCreateDTO,
    ProductVariantUpdateDTO,
    ProductVariantResponseDTO,
)
from app.domain.schemas.paginated_response import PaginatedResponse
from app.core.exceptions import (
    InvalidImageUrlError,
    ServiceUnavailableException,
)
from app.core.security import require_product_owner, get_current_user, User
from app.infrastructure.azure_blob_storage import (
    BlobStorageService,
    InvalidImageError,
    StorageNotConfiguredError,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=PaginatedResponse[ProductListDTO])
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    store_id: UUID | None = Query(None),
    category_id: UUID | None = Query(None),
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    service: ProductService = Depends(get_product_service),
):
    return await service.list_products(
        page=page,
        limit=limit,
        store_id=store_id,
        category_id=category_id,
        is_active=is_active,
        search=search,
        min_price=min_price,
        max_price=max_price,
    )


@router.get("/{product_id}", response_model=ProductDetailResponseDTO)
async def get_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
):
    return await service.get_product_by_id(product_id)


@router.put("/{product_id}", response_model=ProductResponseDTO)
async def update_product(
    product_id: UUID,
    dto: ProductUpdateDTO,
    _: object = Depends(require_product_owner),
    service: ProductService = Depends(get_product_service),
):
    return await service.update_product(product_id, dto)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    _: object = Depends(require_product_owner),
    service: ProductService = Depends(get_product_service),
):
    await service.delete_product(product_id)


@router.post("/{product_id}/favorite", status_code=204)
async def favorite_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    await service.favorite_product(current_user.id, product_id)


@router.delete("/{product_id}/favorite", status_code=204)
async def unfavorite_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    await service.unfavorite_product(current_user.id, product_id)


@router.post(
    "/{product_id}/variants/{variant_id}/images/upload-url",
    response_model=ProductImageUploadResponseDTO,
)
async def create_image_upload_url(
    product_id: UUID,
    variant_id: UUID,
    dto: ProductImageUploadRequestDTO,
    _: object = Depends(require_product_owner),
    storage: BlobStorageService = Depends(get_blob_storage_service),
):
    try:
        upload_url, blob_url, expires_at = storage.generate_upload_sas(
            variant_id, dto.filename, dto.content_type
        )
    except StorageNotConfiguredError as exc:
        raise ServiceUnavailableException(str(exc)) from None
    except InvalidImageError as exc:
        raise InvalidImageUrlError(str(exc)) from None
    return ProductImageUploadResponseDTO(
        upload_url=upload_url, blob_url=blob_url, expires_at=expires_at
    )


@router.post(
    "/{product_id}/variants/{variant_id}/images",
    response_model=ProductImageResponseDTO,
    status_code=201,
)
async def add_product_image(
    product_id: UUID,
    variant_id: UUID,
    dto: ProductImageCreateDTO,
    _: object = Depends(require_product_owner),
    service: ProductImageService = Depends(get_product_image_service),
):
    return await service.add_image(variant_id, dto)


@router.get(
    "/{product_id}/variants/{variant_id}/images",
    response_model=list[ProductImageResponseDTO],
)
async def list_product_images(
    product_id: UUID,
    variant_id: UUID,
    service: ProductImageService = Depends(get_product_image_service),
):
    return await service.list_images(variant_id)


@router.delete("/{product_id}/variants/{variant_id}/images/{image_id}", status_code=204)
async def delete_product_image(
    product_id: UUID,
    variant_id: UUID,
    image_id: UUID,
    _: object = Depends(require_product_owner),
    service: ProductImageService = Depends(get_product_image_service),
):
    await service.delete_image(variant_id, image_id)


@router.patch(
    "/{product_id}/variants/{variant_id}/images/{image_id}/primary",
    status_code=200,
)
async def set_primary_image(
    product_id: UUID,
    variant_id: UUID,
    image_id: UUID,
    _: object = Depends(require_product_owner),
    service: ProductImageService = Depends(get_product_image_service),
):
    await service.set_primary(variant_id, image_id)
    return {"detail": "Primary image updated"}


@router.post(
    "/{product_id}/variants",
    response_model=ProductVariantResponseDTO,
    status_code=201,
)
async def add_product_variant(
    product_id: UUID,
    dto: ProductVariantCreateDTO,
    _: object = Depends(require_product_owner),
    service: ProductVariantService = Depends(get_product_variant_service),
):
    return await service.create_variant(product_id, dto)


@router.get(
    "/{product_id}/variants",
    response_model=list[ProductVariantResponseDTO],
)
async def list_product_variants(
    product_id: UUID,
    service: ProductVariantService = Depends(get_product_variant_service),
):
    return await service.list_variants(product_id)


@router.put(
    "/{product_id}/variants/{variant_id}",
    response_model=ProductVariantResponseDTO,
)
async def update_product_variant(
    product_id: UUID,
    variant_id: UUID,
    dto: ProductVariantUpdateDTO,
    _: object = Depends(require_product_owner),
    service: ProductVariantService = Depends(get_product_variant_service),
):
    return await service.update_variant(product_id, variant_id, dto)


@router.delete("/{product_id}/variants/{variant_id}", status_code=204)
async def delete_product_variant(
    product_id: UUID,
    variant_id: UUID,
    _: object = Depends(require_product_owner),
    service: ProductVariantService = Depends(get_product_variant_service),
):
    await service.delete_variant(product_id, variant_id)
