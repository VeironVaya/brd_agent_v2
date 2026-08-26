"""add brd_groups table and conversations.group_id

Revision ID: g1h2i3j4k5l6
Revises: a1c9d3f7e2b4
Create Date: 2026-08-24 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g1h2i3j4k5l6'
down_revision: Union[str, Sequence[str], None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'brd_groups',
        sa.Column('group_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('group_id'),
    )
    op.create_index(op.f('ix_brd_groups_user_id'), 'brd_groups', ['user_id'], unique=False)

    op.add_column(
        'conversations',
        sa.Column('group_id', sa.String(), sa.ForeignKey('brd_groups.group_id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index(op.f('ix_conversations_group_id'), 'conversations', ['group_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_conversations_group_id'), table_name='conversations')
    op.drop_column('conversations', 'group_id')
    op.drop_index(op.f('ix_brd_groups_user_id'), table_name='brd_groups')
    op.drop_table('brd_groups')
