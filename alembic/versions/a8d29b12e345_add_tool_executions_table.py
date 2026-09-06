"""add tool_executions table

Revision ID: a8d29b12e345
Revises: 2edc5bf40f65
Create Date: 2026-09-06 19:43:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a8d29b12e345'
down_revision: Union[str, Sequence[str], None] = '2edc5bf40f65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tool_executions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=True),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('permission_level', sa.String(length=50), nullable=False),
        sa.Column('arguments', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('requires_confirmation', sa.Boolean(), nullable=False),
        sa.Column('confirmation_reason', sa.Text(), nullable=True),
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('executed_by', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tool_executions_session_id'), 'tool_executions', ['session_id'], unique=False)
    op.create_index(op.f('ix_tool_executions_tool_name'), 'tool_executions', ['tool_name'], unique=False)
    op.create_index(op.f('ix_tool_executions_status'), 'tool_executions', ['status'], unique=False)
    op.create_index(op.f('ix_tool_executions_created_at'), 'tool_executions', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tool_executions_created_at'), table_name='tool_executions')
    op.drop_index(op.f('ix_tool_executions_status'), table_name='tool_executions')
    op.drop_index(op.f('ix_tool_executions_tool_name'), table_name='tool_executions')
    op.drop_index(op.f('ix_tool_executions_session_id'), table_name='tool_executions')
    op.drop_table('tool_executions')
