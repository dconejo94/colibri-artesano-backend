"""drop stock column from products

Revision ID: b11626ad2038
Revises: fc2cf7b05360
Create Date: 2026-06-20 12:16:56.252222

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b11626ad2038"
down_revision: Union[str, Sequence[str], None] = "fc2cf7b05360"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop products.stock.

    Stock now lives only on product_variants; the product-level total is derived
    (sum of variants) at read time, never stored.
    """
    op.drop_column("products", "stock")


def downgrade() -> None:
    """Re-add products.stock."""
    op.add_column(
        "products",
        sa.Column(
            "stock",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
