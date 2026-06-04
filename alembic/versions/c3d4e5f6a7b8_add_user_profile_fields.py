"""add_user_profile_fields

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-01 20:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str]] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("users", sa.Column("name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("address", sa.String(), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.String(), nullable=True))
    op.add_column("users", sa.Column("bio", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "bio")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "address")
    op.drop_column("users", "phone")
    op.drop_column("users", "name")
    op.drop_column("users", "is_active")
