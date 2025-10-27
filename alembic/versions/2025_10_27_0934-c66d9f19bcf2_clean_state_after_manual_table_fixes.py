"""Clean state after manual table fixes

Revision ID: c66d9f19bcf2
Revises: d0718e5ae999
Create Date: 2025-10-27 09:34:24.008378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c66d9f19bcf2'
down_revision: Union[str, None] = 'd0718e5ae999'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
