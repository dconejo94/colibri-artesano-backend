"""move product images to variants

Revision ID: 3be7a9d3f136
Revises: b11626ad2038
Create Date: 2026-06-20 12:45:17.125189

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3be7a9d3f136"
down_revision: Union[str, Sequence[str], None] = "b11626ad2038"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Re-parent product images from products to variants.

    Images now belong to a variant (the sellable unit). The database holds no
    image data yet, so the old product_id column is dropped and a non-null
    variant_id FK is added without a backfill step.
    """
    op.drop_constraint(
        "product_images_product_id_fkey", "product_images", type_="foreignkey"
    )
    op.drop_column("product_images", "product_id")
    op.add_column(
        "product_images",
        sa.Column("variant_id", sa.Uuid(), nullable=False),
    )
    op.create_foreign_key(
        "product_images_variant_id_fkey",
        "product_images",
        "product_variants",
        ["variant_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Re-parent product images back to products."""
    op.drop_constraint(
        "product_images_variant_id_fkey", "product_images", type_="foreignkey"
    )
    op.drop_column("product_images", "variant_id")
    op.add_column(
        "product_images",
        sa.Column("product_id", sa.Uuid(), nullable=False),
    )
    op.create_foreign_key(
        "product_images_product_id_fkey",
        "product_images",
        "products",
        ["product_id"],
        ["id"],
        ondelete="CASCADE",
    )
