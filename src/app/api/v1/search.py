from fastapi import APIRouter, Depends, Query

from app.services.search_service import SearchService
from app.api.deps import get_search_service
from app.domain.schemas.product import ProductListDTO
from app.domain.schemas.search import ProductAutocompleteDTO
from app.domain.schemas.paginated_response import PaginatedResponse

# The prefix intentionally mirrors the products router so that the resulting
# paths are /api/v1/products/search and /api/v1/products/autocomplete.
# This router MUST be registered in __init__.py *before* the products router
# so that FastAPI resolves these literal paths before the /{product_id}
# wildcard route.
router = APIRouter(prefix="/products", tags=["Search"])


@router.get("/search", response_model=PaginatedResponse[ProductListDTO])
async def search_products(
    q: str = Query("", description="Search term (name or description)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Results per page"),
    service: SearchService = Depends(get_search_service),
) -> PaginatedResponse[ProductListDTO]:
    """Full-text product search.

    Searches across product **name** and **description** using trigram
    similarity on PostgreSQL (GIN index) and case-insensitive LIKE on SQLite
    (test environment).  Only active products are returned by default.

    Returns an empty paginated response when *q* is blank.
    """
    return await service.search_products(query=q, page=page, limit=limit)


@router.get("/autocomplete", response_model=list[ProductAutocompleteDTO])
async def autocomplete_products(
    q: str = Query("", description="Partial search term"),
    service: SearchService = Depends(get_search_service),
) -> list[ProductAutocompleteDTO]:
    """Lightweight product autocomplete suggestions.

    Returns at most **10** suggestions with minimal fields (``id``, ``name``,
    ``base_price``, ``primary_image_url``) optimised for search-as-you-type
    widgets.  Only active products are returned.

    Returns an empty array when *q* is blank.
    """
    return await service.autocomplete_products(query=q)
