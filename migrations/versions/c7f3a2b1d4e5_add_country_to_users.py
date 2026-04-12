"""add country to users

Revision ID: c7f3a2b1d4e5
Revises: b4c8e1d0f2a3
Create Date: 2026-04-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7f3a2b1d4e5"
down_revision: Union[str, Sequence[str], None] = "b4c8e1d0f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "country",
            sa.String(length=2),
            nullable=False,
            server_default="HN",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "country")
