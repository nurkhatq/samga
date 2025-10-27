"""fix magistracy type to varchar

Revision ID: d0718e5ae999
Revises: adca3579bf61
Create Date: 2025-10-27 09:26:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d0718e5ae999"
down_revision = "adca3579bf61"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Пустая миграция - ничего не делаем
    pass


def downgrade() -> None:
    # Пустая миграция - ничего не делаем
    pass
