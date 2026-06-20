"""Add Stock to Products table

Revision ID: fc2cf7b05360
Revises: d1e2f3a4b5c6
Create Date: 2026-06-19 00:00:21.301480

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fc2cf7b05360"
down_revision: Union[str, Sequence[str], None] = "932040e62576"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "products",
        sa.Column("stock", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("products", "stock")