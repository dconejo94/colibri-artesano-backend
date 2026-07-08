from uuid import UUID

from app.domain.models.store import Store
from app.domain.schemas.store import StoreCreateDTO, StoreUpdateDTO
from app.domain.schemas.paginated_response import PaginatedResponse
from app.domain.schemas.store import StoreResponseDTO
from app.domain.schemas.vendor import StoreProfileDTO
from app.repositories.store_repository import StoreRepository
from app.core.exceptions import NotFoundException, ConflictException


class StoreService:
    def __init__(self, repository: StoreRepository):
        self.repository = repository

    async def create_store(self, dto: StoreCreateDTO) -> Store:
        existing = await self.repository.get_by_owner_id(dto.owner_id)
        if existing:
            raise ConflictException("El usuario ya tiene una tienda")

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

    async def get_store_profile(
        self, store_id: UUID, current_user_id: UUID | None = None
    ) -> StoreProfileDTO:
        result = await self.repository.get_profile_stats(store_id, current_user_id)
        if not result:
            raise NotFoundException("Store", str(store_id))
        store, product_count, follower_count, is_following = result
        return StoreProfileDTO(
            id=store.id,
            name=store.name,
            description=store.description,
            product_count=product_count,
            follower_count=follower_count,
            is_following=is_following,
        )

    async def follow_store(self, store_id: UUID, user_id: UUID) -> None:
        store = await self.repository.get_by_id(store_id)
        if not store:
            raise NotFoundException("Store", str(store_id))
        is_following = await self.repository.is_following(store_id, user_id)
        if is_following:
            raise ConflictException("Ya sigues esta tienda")
        await self.repository.add_follower(store_id, user_id)

    async def unfollow_store(self, store_id: UUID, user_id: UUID) -> None:
        store = await self.repository.get_by_id(store_id)
        if not store:
            raise NotFoundException("Store", str(store_id))
        await self.repository.remove_follower(store_id, user_id)
