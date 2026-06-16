from app.core.exceptions import AuthenticationException, ConflictException
from app.core.security import (
    REFRESH_TOKEN_TYPE,
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.domain.models.store import Store
from app.domain.models.user import User
from app.domain.schemas.auth import (
    AccessTokenResponseDTO,
    LoginDTO,
    RefreshDTO,
    RegisterDTO,
    TokenResponseDTO,
)
from app.repositories.store_repository import StoreRepository
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(
        self, user_repository: UserRepository, store_repository: StoreRepository
    ):
        self.users = user_repository
        self.stores = store_repository

    async def register(self, dto: RegisterDTO) -> TokenResponseDTO:
        if await self.users.get_by_email(dto.email) is not None:
            raise ConflictException("Email already registered")

        user = User(
            email=dto.email,
            password_hash=hash_password(dto.password),
            name=dto.name,
            role=dto.role,
        )
        user = await self.users.create(user)

        if dto.role == "vendor":
            await self.stores.create(Store(owner_id=user.id, name=dto.store_name))

        return self._issue_tokens(user)

    async def login(self, dto: LoginDTO) -> TokenResponseDTO:
        user = await self.users.get_by_email(dto.email)
        if user is None or not verify_password(dto.password, user.password_hash):
            raise AuthenticationException("Invalid email or password")
        if not user.is_active:
            raise AuthenticationException("Account is inactive")
        return self._issue_tokens(user)

    async def refresh(self, dto: RefreshDTO) -> AccessTokenResponseDTO:
        try:
            user_id = decode_token(dto.refresh_token, expected_type=REFRESH_TOKEN_TYPE)
        except TokenError as exc:
            raise AuthenticationException(str(exc))

        user = await self.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationException("Invalid refresh token")

        return AccessTokenResponseDTO(access_token=create_access_token(user.id))

    def _issue_tokens(self, user: User) -> TokenResponseDTO:
        return TokenResponseDTO(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
