from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Add only the question_metadata column
    op.add_column('questions', 
        sa.Column('question_metadata', postgresql.JSONB(), 
                 nullable=False, server_default='{}')
    )

def downgrade():
    # Remove only the question_metadata column
    op.drop_column('questions', 'question_metadata')