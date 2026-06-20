"""seed default variant for variantless products

Revision ID: 2b926408fbf9
Revises: fc2cf7b05360
Create Date: 2026-06-20 11:56:31.427088

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2b926408fbf9"
down_revision: Union[str, Sequence[str], None] = "fc2cf7b05360"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Give every variantless product a default, sellable variant.

    The variant is the unit that carries stock and price, so a product without
    one cannot be added to a cart. Existing products predating this rule get a
    single "Único" variant (zero modifier, zero stock until a real count is set).
    """
    op.execute(
        sa.text(
            """
            INSERT INTO product_variants
                (id, product_id, name, value, price_modifier, stock_quantity)
            SELECT gen_random_uuid(), p.id, 'Default', 'Único', 0, 0
            FROM products p
            WHERE NOT EXISTS (
                SELECT 1 FROM product_variants v WHERE v.product_id = p.id
            )
            """
        )
    )


def downgrade() -> None:
    """Remove the auto-seeded default variants.

    Only removes variants that still match the seeded default and are the sole
    variant of their product, to avoid deleting real variants added since.
    """
    op.execute(
        sa.text(
            """
            DELETE FROM product_variants v
            WHERE v.name = 'Default'
              AND v.value = 'Único'
              AND v.price_modifier = 0
              AND v.stock_quantity = 0
              AND (
                SELECT COUNT(*) FROM product_variants v2
                WHERE v2.product_id = v.product_id
              ) = 1
            """
        )
    )
