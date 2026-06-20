from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.product import Product
from app.repositories.search_repository import ProductSearchRepository


class SQLAlchemyProductSearchRepository(ProductSearchRepository):
    """SQLAlchemy implementation of ``ProductSearchRepository``.

    ## Cross-database strategy (Option A)

    The search predicate uses ``ILIKE '%query%'`` which:
    * Works on **SQLite** (used by the test suite) via SQLAlchemy's automatic
      ``lower()`` translation — no special driver support needed.
    * Is accelerated on **PostgreSQL** by the ``gin_trgm_ops`` GIN indexes
      added by the Alembic migration ``d1e2f3a4b5c6``.  With those indexes in
      place PostgreSQL reuses the trigram index for LIKE/ILIKE patterns that
      are 3+ characters long, hitting the <300 ms / ~1 s latency targets.

    No dialect-specific SQL is emitted here, so the same class works in both
    environments without a conditional branch.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _base_stmt(self, query: str, is_active: bool):
        """Build the shared WHERE clause used by both methods."""
        pattern = f"%{query}%"
        return (
            select(Product)
            .where(Product.is_active == is_active)
            .where(
                or_(
                    Product.name.ilike(pattern),
                    Product.description.ilike(pattern),
                )
            )
        )

    # ------------------------------------------------------------------
    # ProductSearchRepository interface
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        page: int,
        limit: int,
        is_active: bool = True,
    ) -> tuple[list[Product], int]:
        if not query.strip():
            return [], 0

        base = self._base_stmt(query, is_active)

        # Count total matches without pagination
        count_result = await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = count_result.scalar() or 0

        # Fetch the requested page with all relationships eagerly loaded
        result = await self.db.execute(
            base.options(
                selectinload(Product.store),
                selectinload(Product.category),
                selectinload(Product.images),
                # Needed to derive the product's ``stock`` total without a lazy
                # load during serialization.
                selectinload(Product.variants),
            )
            .order_by(Product.name)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list(result.scalars().all())
        return items, total

    async def autocomplete(
        self,
        query: str,
        limit: int = 10,
        is_active: bool = True,
    ) -> list[Product]:
        if not query.strip():
            return []

        # For autocomplete we only need names + cover images; variants and
        # store info are skipped to minimise query weight.
        result = await self.db.execute(
            self._base_stmt(query, is_active)
            .options(selectinload(Product.images))
            .order_by(Product.name)
            .limit(limit)
        )
        return list(result.scalars().all())
