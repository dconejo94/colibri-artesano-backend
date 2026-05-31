from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from app.services.product_service import ProductService
from app.services.product_image_service import ProductImageService
from app.services.product_variant_service import ProductVariantService
from app.api.deps import (
    get_product_service,
    get_product_image_service,
    get_product_variant_service,
)
from app.domain.schemas.product import (
    ProductUpdateDTO,
    ProductResponseDTO,
    ProductDetailResponseDTO,
)
from app.domain.schemas.product_image import (
    ProductImageCreateDTO,
    ProductImageResponseDTO,
)
from app.domain.schemas.product_variant import (
    ProductVariantCreateDTO,
    ProductVariantUpdateDTO,
    ProductVariantResponseDTO,
)
from app.domain.schemas.paginated_response import PaginatedResponse
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/products", tags=["Products"])


# ── Product CRUD ──────────────────────────────────────────────────

@router.get("/", response_model=PaginatedResponse[ProductResponseDTO])
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category_id: UUID | None = None,
    is_active: bool | None = None,
    service: ProductService = Depends(get_product_service),
):
    return await service.list_products(
        page=page, limit=limit, category_id=category_id, is_active=is_active
    )


@router.get("/{product_id}", response_model=ProductDetailResponseDTO)
async def get_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
):
    try:
        return await service.get_product_by_id(product_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Product not found")


@router.put("/{product_id}", response_model=ProductResponseDTO)
async def update_product(
    product_id: UUID,
    dto: ProductUpdateDTO,
    service: ProductService = Depends(get_product_service),
):
    try:
        return await service.update_product(product_id, dto)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Product not found")


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
):
    try:
        await service.delete_product(product_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Product not found")


# ── Product Images ────────────────────────────────────────────────

@router.post(
    "/{product_id}/images",
    response_model=ProductImageResponseDTO,
    status_code=201,
)
async def add_product_image(
    product_id: UUID,
    dto: ProductImageCreateDTO,
    service: ProductImageService = Depends(get_product_image_service),
):
    return await service.add_image(product_id, dto)


@router.get(
    "/{product_id}/images",
    response_model=list[ProductImageResponseDTO],
)
async def list_product_images(
    product_id: UUID,
    service: ProductImageService = Depends(get_product_image_service),
):
    return await service.list_images(product_id)


@router.delete("/{product_id}/images/{image_id}", status_code=204)
async def delete_product_image(
    product_id: UUID,
    image_id: UUID,
    service: ProductImageService = Depends(get_product_image_service),
):
    try:
        await service.delete_image(image_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Image not found")


@router.patch("/{product_id}/images/{image_id}/primary", status_code=200)
async def set_primary_image(
    product_id: UUID,
    image_id: UUID,
    service: ProductImageService = Depends(get_product_image_service),
):
    try:
        await service.set_primary(product_id, image_id)
        return {"detail": "Primary image updated"}
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Image not found")


# ── Product Variants ──────────────────────────────────────────────

@router.post(
    "/{product_id}/variants",
    response_model=ProductVariantResponseDTO,
    status_code=201,
)
async def add_product_variant(
    product_id: UUID,
    dto: ProductVariantCreateDTO,
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
    service: ProductVariantService = Depends(get_product_variant_service),
):
    try:
        return await service.update_variant(variant_id, dto)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Variant not found")


@router.delete("/{product_id}/variants/{variant_id}", status_code=204)
async def delete_product_variant(
    product_id: UUID,
    variant_id: UUID,
    service: ProductVariantService = Depends(get_product_variant_service),
):
    try:
        await service.delete_variant(variant_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Variant not found")
