from uuid import UUID

from app.domain.models.product import Product
from app.domain.schemas.product import ProductCreateDTO, ProductUpdateDTO
from app.domain.schemas.paginated_response import PaginatedResponse
from app.domain.schemas.product import ProductResponseDTO
from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.core.exceptions import NotFoundException


class ProductService:
    def __init__(
        self,
        repository: ProductRepository,
        category_repository: CategoryRepository,
    ):
        self.repository = repository
        self.category_repo = category_repository

    async def create_product(self, store_id: UUID, dto: ProductCreateDTO) -> Product:
        category = await self.category_repo.get_by_id(dto.category_id)
        if not category:
            raise NotFoundException("Category", str(dto.category_id))

        product = Product(
            store_id=store_id,
            category_id=dto.category_id,
            name=dto.name,
            description=dto.description,
            base_price=dto.base_price,
            is_active=dto.is_active,
        )
        return await self.repository.create(product)

    async def list_products(
        self,
        page: int,
        limit: int,
        store_id: UUID | None = None,
        category_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> PaginatedResponse[ProductResponseDTO]:
        items, total = await self.repository.list_products(
            page, limit, store_id=store_id, category_id=category_id, is_active=is_active
        )
        return PaginatedResponse(items=items, page=page, limit=limit, total=total)

    async def get_product_by_id(self, product_id: UUID) -> Product:
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", str(product_id))
        return product

    async def update_product(self, product_id: UUID, dto: ProductUpdateDTO) -> Product:
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", str(product_id))

        if dto.category_id is not None:
            category = await self.category_repo.get_by_id(dto.category_id)
            if not category:
                raise NotFoundException("Category", str(dto.category_id))

        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        return await self.repository.update(product)

    async def delete_product(self, product_id: UUID) -> None:
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", str(product_id))
        await self.repository.delete(product)
