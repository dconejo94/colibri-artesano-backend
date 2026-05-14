from fastapi import APIRouter, Depends, Query

from app.services.product_service import ProductService
from app.api.deps import get_product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/")
def get_all_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category: str | None = None,
    service: ProductService = Depends(get_product_service),
):
    return service.get_all_products(page=page, limit=limit, category=category)
