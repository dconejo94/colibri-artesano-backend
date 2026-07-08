from typing import Literal, Any
from fastapi import APIRouter, Depends, Query

from app.services.search_service import SearchService
from app.api.deps import get_search_service
from app.domain.schemas.product import ProductListDTO
from app.domain.schemas.search import ProductAutocompleteDTO
from app.domain.schemas.paginated_response import PaginatedResponse

router = APIRouter(tags=["Search"])

SearchScope = Literal["all", "products", "stores", "categories"]


@router.get("/search")
async def unified_search(
    q: str = Query("", description="Search term"),
    scope: SearchScope = Query("all", description="Search scope"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Results per page"),
    service: SearchService = Depends(get_search_service),
) -> Any:
    """Unified full-text search across entities."""
    if len(q) < 2:
        if scope == "all":
            return {"products": [], "stores": [], "categories": []}
        if scope == "categories":
            return []
        return PaginatedResponse(items=[], total=0, page=page, limit=limit)

    if scope == "products":
        return await service.search_products(query=q, page=page, limit=limit)
    elif scope == "stores":
        return await service.search_stores(query=q, page=page, limit=limit)
    elif scope == "categories":
        return await service.search_categories(query=q)
    elif scope == "all":
        products = await service.search_products(query=q, page=1, limit=limit)
        stores = await service.search_stores(query=q, page=1, limit=limit)
        categories = await service.search_categories(query=q)
        return {
            "products": products.items,
            "stores": stores.items,
            "categories": categories,
        }


@router.get("/search/autocomplete")
async def unified_autocomplete(
    q: str = Query("", description="Partial search term"),
    scope: SearchScope = Query("all", description="Search scope"),
    service: SearchService = Depends(get_search_service),
) -> Any:
    """Unified autocomplete suggestions."""
    if len(q) < 2:
        if scope == "all":
            return {"products": [], "stores": [], "categories": []}
        return []

    if scope == "products":
        return await service.autocomplete_products(query=q)
    elif scope == "stores":
        return await service.autocomplete_stores(query=q)
    elif scope == "categories":
        return await service.autocomplete_categories(query=q)
    elif scope == "all":
        products = await service.autocomplete_products(query=q)
        stores = await service.autocomplete_stores(query=q)
        categories = await service.autocomplete_categories(query=q)
        return {
            "products": products,
            "stores": stores,
            "categories": categories,
        }


# Legacy Proxy Endpoints
@router.get("/products/search", response_model=PaginatedResponse[ProductListDTO])
async def search_products_legacy(
    q: str = Query("", description="Search term (name or description)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Results per page"),
    service: SearchService = Depends(get_search_service),
) -> PaginatedResponse[ProductListDTO]:
    return await unified_search(q=q, scope="products", page=page, limit=limit, service=service)


@router.get("/products/autocomplete", response_model=list[ProductAutocompleteDTO])
async def autocomplete_products_legacy(
    q: str = Query("", description="Partial search term"),
    service: SearchService = Depends(get_search_service),
) -> list[ProductAutocompleteDTO]:
    return await unified_autocomplete(q=q, scope="products", service=service)
