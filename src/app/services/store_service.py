from uuid import UUID

from app.domain.models.store import Store
from app.domain.schemas.store import StoreCreateDTO, StoreUpdateDTO
from app.domain.schemas.paginated_response import PaginatedResponse
from app.domain.schemas.store import StoreResponseDTO
from app.domain.schemas.vendor import VendorProfileDTO
from app.repositories.store_repository import StoreRepository
from app.core.exceptions import NotFoundException, ConflictException


class StoreService:
    def __init__(self, repository: StoreRepository):
        self.repository = repository

    async def create_store(self, dto: StoreCreateDTO) -> Store:
        existing = await self.repository.get_by_owner_id(dto.owner_id)
        if existing:
            raise ConflictException("User already owns a store")

        store = Store(
            owner_id=dto.owner_id,
            name=dto.name,
            description=dto.description,
            logo_url=dto.logo_url,
        )
        return await self.repository.create(store)

    async def list_stores(
        self, page: int, limit: int, owner_id: UUID | None = None
    ) -> PaginatedResponse[StoreResponseDTO]:
        items, total = await self.repository.list_stores(page, limit, owner_id)
        return PaginatedResponse(items=items, page=page, limit=limit, total=total)

    async def get_store_by_id(self, store_id: UUID) -> Store:
        store = await self.repository.get_by_id(store_id)
        if not store:
            raise NotFoundException("Store", str(store_id))
        return store

    async def get_store_by_owner_id(self, owner_id: UUID) -> Store:
        store = await self.repository.get_by_owner_id(owner_id)
        if not store:
            raise NotFoundException("Store for Owner", str(owner_id))
        return store

    async def update_store(self, store_id: UUID, dto: StoreUpdateDTO) -> Store:
        store = await self.repository.get_by_id(store_id)
        if not store:
            raise NotFoundException("Store", str(store_id))

        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(store, field, value)

        return await self.repository.update(store)

    async def delete_store(self, store_id: UUID) -> None:
        store = await self.repository.get_by_id(store_id)
        if not store:
            raise NotFoundException("Store", str(store_id))
        await self.repository.delete(store)

    async def get_vendor_profile(self, store_id: UUID) -> VendorProfileDTO:
        result = await self.repository.get_with_product_count(store_id)
        if not result:
            raise NotFoundException("Vendor", str(store_id))
        store, product_count = result
        return VendorProfileDTO(
            id=store.id,
            name=store.name,
            description=store.description,
            product_count=product_count,
        )
