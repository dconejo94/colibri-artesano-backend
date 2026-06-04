from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.user import User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def update(self, user: User, data: dict) -> User: ...

    @abstractmethod
    async def delete(self, user: User) -> None: ...
