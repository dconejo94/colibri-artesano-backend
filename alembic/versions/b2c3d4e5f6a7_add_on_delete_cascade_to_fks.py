"""add_on_delete_cascade_to_fks

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-01 19:15:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str]] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ON DELETE CASCADE / SET NULL to all child FK constraints."""

    # ── products.store_id → CASCADE ───────────────────────────────
    op.drop_constraint("products_store_id_fkey", "products", type_="foreignkey")
    op.create_foreign_key(
        "products_store_id_fkey",
        "products",
        "stores",
        ["store_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ── products.category_id → SET NULL (allow null) ──────────────
    op.drop_constraint("products_category_id_fkey", "products", type_="foreignkey")
    op.alter_column("products", "category_id", nullable=True)
    op.create_foreign_key(
        "products_category_id_fkey",
        "products",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ── product_images.product_id → CASCADE ───────────────────────
    op.drop_constraint(
        "product_images_product_id_fkey", "product_images", type_="foreignkey"
    )
    op.create_foreign_key(
        "product_images_product_id_fkey",
        "product_images",
        "products",
        ["product_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ── product_variants.product_id → CASCADE ─────────────────────
    op.drop_constraint(
        "product_variants_product_id_fkey", "product_variants", type_="foreignkey"
    )
    op.create_foreign_key(
        "product_variants_product_id_fkey",
        "product_variants",
        "products",
        ["product_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ── store_orders.main_order_id → CASCADE ──────────────────────
    op.drop_constraint(
        "store_orders_main_order_id_fkey", "store_orders", type_="foreignkey"
    )
    op.create_foreign_key(
        "store_orders_main_order_id_fkey",
        "store_orders",
        "main_orders",
        ["main_order_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ── order_items.store_order_id → CASCADE ──────────────────────
    op.drop_constraint(
        "order_items_store_order_id_fkey", "order_items", type_="foreignkey"
    )
    op.create_foreign_key(
        "order_items_store_order_id_fkey",
        "order_items",
        "store_orders",
        ["store_order_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Remove ON DELETE actions from FK constraints."""

    # ── order_items.store_order_id ────────────────────────────────
    op.drop_constraint(
        "order_items_store_order_id_fkey", "order_items", type_="foreignkey"
    )
    op.create_foreign_key(
        "order_items_store_order_id_fkey",
        "order_items",
        "store_orders",
        ["store_order_id"],
        ["id"],
    )

    # ── store_orders.main_order_id ────────────────────────────────
    op.drop_constraint(
        "store_orders_main_order_id_fkey", "store_orders", type_="foreignkey"
    )
    op.create_foreign_key(
        "store_orders_main_order_id_fkey",
        "store_orders",
        "main_orders",
        ["main_order_id"],
        ["id"],
    )

    # ── product_variants.product_id ───────────────────────────────
    op.drop_constraint(
        "product_variants_product_id_fkey", "product_variants", type_="foreignkey"
    )
    op.create_foreign_key(
        "product_variants_product_id_fkey",
        "product_variants",
        "products",
        ["product_id"],
        ["id"],
    )

    # ── product_images.product_id ─────────────────────────────────
    op.drop_constraint(
        "product_images_product_id_fkey", "product_images", type_="foreignkey"
    )
    op.create_foreign_key(
        "product_images_product_id_fkey",
        "product_images",
        "products",
        ["product_id"],
        ["id"],
    )

    # ── products.category_id ─────────────────────────────────────
    op.drop_constraint("products_category_id_fkey", "products", type_="foreignkey")
    op.alter_column("products", "category_id", nullable=False)
    op.create_foreign_key(
        "products_category_id_fkey",
        "products",
        "categories",
        ["category_id"],
        ["id"],
    )

    # ── products.store_id ─────────────────────────────────────────
    op.drop_constraint("products_store_id_fkey", "products", type_="foreignkey")
    op.create_foreign_key(
        "products_store_id_fkey",
        "products",
        "stores",
        ["store_id"],
        ["id"],
    )
