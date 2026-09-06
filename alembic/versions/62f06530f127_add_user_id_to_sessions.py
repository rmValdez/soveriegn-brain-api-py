"""add_user_id_to_sessions

Revision ID: 62f06530f127
Revises: a8d29b12e345
Create Date: 2026-09-06 12:51:18.227078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62f06530f127'
down_revision: Union[str, Sequence[str], None] = 'a8d29b12e345'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("sessions", sa.Column("user_id", sa.String(), nullable=True))
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_column("sessions", "user_id")
