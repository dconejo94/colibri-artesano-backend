from app.domain.schemas.paginated_response import PaginatedResponse
from app.domain.schemas.product import ProductListDTO
from app.domain.schemas.store import StoreResponseDTO, StoreAutocompleteDTO
from app.domain.schemas.category import CategoryResponseDTO, CategoryAutocompleteDTO
from app.domain.schemas.search import ProductAutocompleteDTO
from app.repositories.search_repository import (
    ProductSearchRepository,
    StoreSearchRepository,
    CategorySearchRepository,
)

_AUTOCOMPLETE_MAX = 10


class SearchService:
    def __init__(
        self,
        repository: ProductSearchRepository,
        store_repository: StoreSearchRepository,
        category_repository: CategorySearchRepository,
    ) -> None:
        self.repository = repository
        self.store_repository = store_repository
        self.category_repository = category_repository

    async def search_products(
        self,
        query: str,
        page: int,
        limit: int,
        is_active: bool = True,
    ) -> PaginatedResponse[ProductListDTO]:
        items, total = await self.repository.search(
            query=query,
            page=page,
            limit=limit,
            is_active=is_active,
        )
        return PaginatedResponse(items=items, page=page, limit=limit, total=total)

    async def autocomplete_products(
        self,
        query: str,
        is_active: bool = True,
    ) -> list[ProductAutocompleteDTO]:
        items = await self.repository.autocomplete(
            query=query,
            limit=_AUTOCOMPLETE_MAX,
            is_active=is_active,
        )
        return [ProductAutocompleteDTO.model_validate(item) for item in items]

    async def search_stores(
        self,
        query: str,
        page: int,
        limit: int,
    ) -> PaginatedResponse[StoreResponseDTO]:
        items, total = await self.store_repository.search(query, page, limit)
        return PaginatedResponse(items=items, page=page, limit=limit, total=total)

    async def autocomplete_stores(self, query: str) -> list[StoreAutocompleteDTO]:
        items = await self.store_repository.autocomplete(query, _AUTOCOMPLETE_MAX)
        return [StoreAutocompleteDTO.model_validate(item) for item in items]

    async def search_categories(self, query: str) -> list[CategoryResponseDTO]:
        items = await self.category_repository.search(query)
        return [CategoryResponseDTO.model_validate(item) for item in items]

    async def autocomplete_categories(
        self, query: str
    ) -> list[CategoryAutocompleteDTO]:
        items = await self.category_repository.autocomplete(query, _AUTOCOMPLETE_MAX)
        return [CategoryAutocompleteDTO.model_validate(item) for item in items]
