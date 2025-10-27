"""Add question_metadata column to questions

Revision ID: adca3579bf61
Revises: c8db65e354ab
Create Date: 2025-10-27 06:39:01.089643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'adca3579bf61'
down_revision: Union[str, None] = 'c8db65e354ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add only the question_metadata column
    op.add_column('questions', 
        sa.Column('question_metadata', postgresql.JSONB(), 
                 nullable=False, server_default='{}')
    )


def downgrade() -> None:
    # Remove only the question_metadata column
    op.drop_column('questions', 'question_metadata')