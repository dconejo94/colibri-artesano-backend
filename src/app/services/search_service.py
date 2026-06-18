from app.domain.schemas.paginated_response import PaginatedResponse
from app.domain.schemas.product import ProductListDTO
from app.domain.schemas.search import ProductAutocompleteDTO
from app.repositories.search_repository import ProductSearchRepository

_AUTOCOMPLETE_MAX = 10


class SearchService:
    """Orchestrates product search and autocomplete use-cases.

    Accepts any ``ProductSearchRepository`` implementation, which makes the
    service fully testable in isolation and ready for dependency injection.
    Future feature teams (e.g. a store or category search) can inject a
    different repository implementation into a similar service without
    modifying this class.
    """

    def __init__(self, repository: ProductSearchRepository) -> None:
        self.repository = repository

    async def search_products(
        self,
        query: str,
        page: int,
        limit: int,
        is_active: bool = True,
    ) -> PaginatedResponse[ProductListDTO]:
        """Full-text search with pagination.

        Returns an empty paginated response when *query* is blank so the
        endpoint never errors on a missing query parameter.
        """
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
        """Fast prefix/trigram suggestions, hard-capped at 10 results.

        Returns an empty list when *query* is blank — the caller should not
        fire this endpoint before the user has typed at least one character.
        """
        items = await self.repository.autocomplete(
            query=query,
            limit=_AUTOCOMPLETE_MAX,
            is_active=is_active,
        )
        return [ProductAutocompleteDTO.model_validate(item) for item in items]
