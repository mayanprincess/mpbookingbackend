"""agregando nuevos campos a la tabla de reservas

Revision ID: 3d61c43ffc71
Revises: 0cdb4a7196be
Create Date: 2026-01-14 10:19:20.517597

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d61c43ffc71'
down_revision: Union[str, Sequence[str], None] = '0cdb4a7196be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Los campos isPaid, createdAt, reservationId y confirmationNumber
    # ya fueron agregados en la migración 1c2f4428e60a, por lo que no se agregan aquí
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # Los campos isPaid, createdAt, reservationId y confirmationNumber
    # ya fueron agregados en la migración 1c2f4428e60a, por lo que no se eliminan aquí
    pass
