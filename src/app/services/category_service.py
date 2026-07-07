from uuid import UUID

from app.domain.models.category import Category
from app.domain.schemas.category import CategoryCreateDTO, CategoryUpdateDTO
from app.repositories.category_repository import CategoryRepository
from app.core.exceptions import NotFoundException, ConflictException


class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    async def create_category(self, dto: CategoryCreateDTO) -> Category:
        existing = await self.repository.get_by_slug(dto.slug)
        if existing:
            raise ConflictException(f"Ya existe una categoría con el slug '{dto.slug}'")
        category = Category(name=dto.name, slug=dto.slug)
        return await self.repository.create(category)

    async def list_categories(self) -> list[Category]:
        return await self.repository.list_all()

    async def get_category_by_id(self, category_id: UUID) -> Category:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", str(category_id))
        return category

    async def update_category(
        self, category_id: UUID, dto: CategoryUpdateDTO
    ) -> Category:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", str(category_id))

        if dto.slug:
            existing = await self.repository.get_by_slug(dto.slug)
            if existing and existing.id != category_id:
                raise ConflictException(
                    f"Ya existe una categoría con el slug '{dto.slug}'"
                )

        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        return await self.repository.update(category)

    async def delete_category(self, category_id: UUID) -> None:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", str(category_id))
        await self.repository.delete(category)
