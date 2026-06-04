from app.domain.models.user import User
from app.domain.schemas.user import UserUpdateDTO
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_me(self, user: User) -> User:
        return user

    async def update_me(self, user: User, data: UserUpdateDTO) -> User:
        update_data = data.model_dump(exclude_none=True)
        return await self.repository.update(user, update_data)

    async def delete_me(self, user: User) -> None:
        await self.repository.delete(user)
