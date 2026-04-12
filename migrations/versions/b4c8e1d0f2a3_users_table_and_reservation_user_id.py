"""users table and reservation user_id

Revision ID: b4c8e1d0f2a3
Revises: 022aaa3c9a9b
Create Date: 2026-04-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b4c8e1d0f2a3"
down_revision: Union[str, Sequence[str], None] = "022aaa3c9a9b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=64), nullable=False),
        sa.Column("national_id", sa.String(length=128), nullable=False),
        sa.Column("points_balance", sa.Integer(), nullable=False),
        sa.Column("membership_tier", sa.String(length=32), nullable=False),
        sa.Column("reservation_count", sa.Integer(), nullable=False),
        sa.Column("account_verified", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.add_column(
        "reservations",
        sa.Column("user_id", sa.String(length=36), nullable=True),
    )
    op.create_index("ix_reservations_user_id", "reservations", ["user_id"])
    op.create_foreign_key(
        "fk_reservations_user_id_users",
        "reservations",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_reservations_user_id_users", "reservations", type_="foreignkey")
    op.drop_index("ix_reservations_user_id", table_name="reservations")
    op.drop_column("reservations", "user_id")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
