from logging.config import fileConfig
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import create_engine, pool
from alembic import context

from app.config import settings
from app.core.database import Base
import app.domain.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    """Resolve the migration database URL.

    Prefers the ``DATABASE_URL`` environment variable (used by CI to inject
    admin credentials for the hosted database); falls back to the URL built
    from local settings so developers need no extra configuration.
    """
    return os.environ.get("DATABASE_URL") or settings.SYNC_DATABASE_URL


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(get_database_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
