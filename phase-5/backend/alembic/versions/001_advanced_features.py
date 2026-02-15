"""Initial migration for Phase V Part A - Advanced Features

Revision ID: 001_advanced_features
Revises: 
Create Date: 2026-02-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
import uuid
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_advanced_features'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the task table with advanced features
    op.create_table('task',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('recurring_task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['recurring_task_id'], ['recurringtask.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create the recurringtask table
    op.create_table('recurringtask',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('recurrence_pattern', sa.String(), nullable=False),
        sa.Column('custom_interval', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('max_instances', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('idx_task_priority', 'task', ['priority'])
    op.create_index('idx_task_due_date', 'task', ['due_date'])
    op.create_index('idx_task_created_at', 'task', ['created_at'])
    op.create_index('idx_task_status', 'task', ['status'])
    op.create_index('idx_recurring_task_pattern', 'recurringtask', ['recurrence_pattern'])
    op.create_index('idx_recurring_task_active', 'recurringtask', ['is_active'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_recurring_task_active', table_name='recurringtask')
    op.drop_index('idx_recurring_task_pattern', table_name='recurringtask')
    op.drop_index('idx_task_status', table_name='task')
    op.drop_index('idx_task_created_at', table_name='task')
    op.drop_index('idx_task_due_date', table_name='task')
    op.drop_index('idx_task_priority', table_name='task')
    
    # Drop tables
    op.drop_table('recurringtask')
    op.drop_table('task')