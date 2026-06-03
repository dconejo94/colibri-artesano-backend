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
