from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException


from app.services.product_service import ProductService
from app.api.deps import get_product_service

from app.domain.schemas.paginated_response import PaginatedProductsResponseDTO
from app.domain.schemas.product import ProductResponseDTO

from app.core.exceptions import ProductNotFoundException

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=PaginatedProductsResponseDTO)
async def get_all_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category: str | None = None,
    service: ProductService = Depends(get_product_service),
):
    return await service.get_all_products(page=page, limit=limit, category=category)


@router.get("/{id}", response_model=ProductResponseDTO)
async def get_product_by_id(
    id: int,
    service: ProductService = Depends(get_product_service),
):
    try:
        product = await service.get_product_by_id(id)
        return ProductResponseDTO.model_validate(product)

    except ProductNotFoundException:
        raise HTTPException(status_code=404, detail="Product not found")
