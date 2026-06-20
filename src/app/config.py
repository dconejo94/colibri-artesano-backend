from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    APP_NAME: str = "Colibri Artesano API"

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "colibri"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    SQL_ECHO: bool = False
    # SSL mode for the database connection. Use "disable" for local Postgres
    DB_SSL_MODE: str = "disable"

    ALLOWED_ORIGINS: list[str] = ["http://localhost:8081"]
    BACKEND_PORT: int = 8000

    # JWT / auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    # Rate limit applied to the login and register endpoints
    AUTH_RATE_LIMIT: str = "5/minute"

    # Azure Blob Storage (product images).
    AZURE_STORAGE_ACCOUNT_NAME: str = ""
    AZURE_STORAGE_ACCOUNT_KEY: str = ""
    AZURE_STORAGE_CONTAINER: str = "product-images"
    # Optional endpoint override for Azurite / custom domains.
    AZURE_STORAGE_BLOB_ENDPOINT: str = ""
    # Minutes a generated upload SAS stays valid.
    AZURE_STORAGE_SAS_EXPIRY_MINUTES: int = 15
    # When True, ``POST /images`` only accepts URLs pointing at the configured
    # blob host.
    AZURE_STORAGE_VALIDATE_IMAGE_URL: bool = False

    @property
    def AZURE_STORAGE_CONFIGURED(self) -> bool:
        return bool(self.AZURE_STORAGE_ACCOUNT_NAME and self.AZURE_STORAGE_ACCOUNT_KEY)

    @property
    def AZURE_BLOB_BASE_URL(self) -> str:
        """Public base URL for the storage account (no trailing slash)."""
        if self.AZURE_STORAGE_BLOB_ENDPOINT:
            return self.AZURE_STORAGE_BLOB_ENDPOINT.rstrip("/")
        return f"https://{self.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"

    @property
    def SYNC_DATABASE_URL(self) -> str:
        # psycopg understands the ``sslmode`` query parameter.
        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
            f"?sslmode={self.DB_SSL_MODE}"
        )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        # asyncpg uses ``ssl`` (not ``sslmode``) for the same set of modes.
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
            f"?ssl={self.DB_SSL_MODE}"
        )


settings = Settings()
