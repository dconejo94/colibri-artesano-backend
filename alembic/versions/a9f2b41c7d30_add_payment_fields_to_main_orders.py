"""add payment fields to main orders

Revision ID: a9f2b41c7d30
Revises: dd192fecc0c6
Create Date: 2026-07-09 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a9f2b41c7d30"
down_revision: Union[str, Sequence[str], None] = "dd192fecc0c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # NOT NULL with a server_default so existing rows are backfilled atomically.
    # The default is kept: "pending" is the correct state for any new order.
    op.add_column(
        "main_orders",
        sa.Column(
            "payment_status", sa.String(), nullable=False, server_default="pending"
        ),
    )
    op.add_column(
        "main_orders",
        sa.Column("payment_method", sa.String(), nullable=True),
    )
    # Stripe PaymentIntent id; nullable because carts have no payment yet.
    op.add_column(
        "main_orders",
        sa.Column("payment_reference", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("main_orders", "payment_reference")
    op.drop_column("main_orders", "payment_method")
    op.drop_column("main_orders", "payment_status")
