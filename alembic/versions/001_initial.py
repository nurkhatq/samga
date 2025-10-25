"""
Initial migration - create all tables

Revision ID: 001_initial
Create Date: 2025-10-25 06:30:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables"""
    
    # ===================================
    # 1. Users table
    # ===================================
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('role', sa.Enum('student', 'admin', 'moderator', name='userrole'), nullable=False),
        sa.Column('major_code', sa.String(length=10), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_role', 'users', ['role'])
    
    # ===================================
    # 2. Majors table
    # ===================================
    op.create_table(
        'majors',
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('title_kk', sa.String(length=500), nullable=False),
        sa.Column('title_ru', sa.String(length=500), nullable=False),
        sa.Column('magistracy_type', sa.Enum('profile', 'scientific', name='magistracytype'), nullable=False),
        sa.Column('categories', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('code')
    )
    op.create_index('ix_majors_magistracy_type', 'majors', ['magistracy_type'])
    
    # ===================================
    # 3. Subjects table
    # ===================================
    op.create_table(
        'subjects',
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('title_kk', sa.String(length=300), nullable=False),
        sa.Column('title_ru', sa.String(length=300), nullable=False),
        sa.Column('subject_type', sa.Enum('common', 'profile', name='subjecttype'), nullable=False),
        sa.Column('major_code', sa.String(length=10), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('code'),
        sa.ForeignKeyConstraint(['major_code'], ['majors.code'], ondelete='CASCADE')
    )
    op.create_index('ix_subjects_subject_type', 'subjects', ['subject_type'])
    op.create_index('ix_subjects_major_code', 'subjects', ['major_code'])
    
    # ===================================
    # 4. Questions table
    # ===================================
    op.create_table(
        'questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subject_code', sa.String(length=50), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('difficulty', sa.Enum('easy', 'medium', 'hard', name='questiondifficulty'), nullable=False),
        sa.Column('question_type', sa.Enum('single', 'multiple', name='questiontype'), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('time_seconds', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['subject_code'], ['subjects.code'], ondelete='CASCADE')
    )
    op.create_index('ix_questions_subject_code', 'questions', ['subject_code'])
    op.create_index('ix_questions_difficulty', 'questions', ['difficulty'])
    op.create_index('ix_questions_question_type', 'questions', ['question_type'])
    
    # ===================================
    # 5. Exam Attempts table
    # ===================================
    op.create_table(
        'exam_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mode', sa.Enum('practice', 'exam', name='exammode'), nullable=False),
        sa.Column('major_code', sa.String(length=10), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('time_limit_minutes', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('in_progress', 'completed', 'expired', name='examstatus'), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('answered_questions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('correct_answers', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('score_percentage', sa.Float(), nullable=True),
        sa.Column('proctoring_copy_paste_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('proctoring_tab_switches_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('proctoring_console_opens_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('proctoring_suspicious', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['major_code'], ['majors.code'], ondelete='SET NULL')
    )
    op.create_index('ix_exam_attempts_user_id', 'exam_attempts', ['user_id'])
    op.create_index('ix_exam_attempts_status', 'exam_attempts', ['status'])
    op.create_index('ix_exam_attempts_mode', 'exam_attempts', ['mode'])
    op.create_index('ix_exam_attempts_started_at', 'exam_attempts', ['started_at'])
    
    # ===================================
    # 6. Exam Answers table
    # ===================================
    op.create_table(
        'exam_answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attempt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('selected_keys', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('answered_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['attempt_id'], ['exam_attempts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE')
    )
    op.create_index('ix_exam_answers_attempt_id', 'exam_answers', ['attempt_id'])
    op.create_index('ix_exam_answers_question_id', 'exam_answers', ['question_id'])
    
    # ===================================
    # 7. Proctoring Events table
    # ===================================
    op.create_table(
        'proctoring_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attempt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.Enum(
            'copy', 'paste', 'cut', 'tab_switch', 'window_blur',
            'console_open', 'right_click', 'context_menu',
            name='proctoringeventtype'
        ), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('proctoring_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['attempt_id'], ['exam_attempts.id'], ondelete='CASCADE')
    )
    op.create_index('ix_proctoring_events_attempt_id', 'proctoring_events', ['attempt_id'])
    op.create_index('ix_proctoring_events_event_type', 'proctoring_events', ['event_type'])
    op.create_index('ix_proctoring_events_timestamp', 'proctoring_events', ['timestamp'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('proctoring_events')
    op.drop_table('exam_answers')
    op.drop_table('exam_attempts')
    op.drop_table('questions')
    op.drop_table('subjects')
    op.drop_table('majors')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS proctoringeventtype')
    op.execute('DROP TYPE IF EXISTS examstatus')
    op.execute('DROP TYPE IF EXISTS exammode')
    op.execute('DROP TYPE IF EXISTS questiontype')
    op.execute('DROP TYPE IF EXISTS questiondifficulty')
    op.execute('DROP TYPE IF EXISTS subjecttype')
    op.execute('DROP TYPE IF EXISTS magistracytype')
    op.execute('DROP TYPE IF EXISTS userrole')
