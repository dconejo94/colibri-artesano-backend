"""Add pg_trgm GIN indexes for product full-text search.

Enables the ``pg_trgm`` extension (PostgreSQL-only) and adds GIN trigram
indexes on ``products.name`` and ``products.description``.  These indexes
make LIKE / ILIKE queries with a 3+ character pattern use the index rather
than a sequential scan, meeting the latency targets:

* ``GET /api/v1/products/search``     → ~1 s on large datasets
* ``GET /api/v1/products/autocomplete`` → <300 ms

The migration is deliberately safe for the SQLite test database — it wraps
the PostgreSQL-specific DDL in a dialect check so the migration runner does
not fail when executing against SQLite.

Revision ID: d1e2f3a4b5c6
Revises: c3d4e5f6a7b8
Create Date: 2026-06-13
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "d1e2f3a4b5c6"
down_revision = "c97cd381abe6"
branch_labels = None
depends_on = None


def _is_postgresql() -> bool:
    """Return True when the migration is running against a PostgreSQL database."""
    return op.get_bind().dialect.name == "postgresql"


def upgrade() -> None:
    if not _is_postgresql():
        return

    # Enable the trigram extension (idempotent — safe to run more than once).
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # GIN index on product name — powers both search and autocomplete.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_products_name_trgm
        ON products
        USING GIN (name gin_trgm_ops)
        """
    )

    # GIN index on product description — powers the full-text search endpoint.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_products_description_trgm
        ON products
        USING GIN (description gin_trgm_ops)
        """
    )


def downgrade() -> None:
    if not _is_postgresql():
        return

    op.execute("DROP INDEX IF EXISTS ix_products_description_trgm")
    op.execute("DROP INDEX IF EXISTS ix_products_name_trgm")
    # Do NOT drop the pg_trgm extension on downgrade — other indexes or
    # queries in the database may rely on it.
