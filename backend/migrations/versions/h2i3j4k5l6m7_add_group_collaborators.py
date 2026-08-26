"""add group_collaborators table

Revision ID: h2i3j4k5l6m7
Revises: g1h2i3j4k5l6
Create Date: 2026-08-24 10:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h2i3j4k5l6m7'
down_revision: Union[str, Sequence[str], None] = 'g1h2i3j4k5l6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'group_collaborators',
        sa.Column('group_collaborator_id', sa.String(), nullable=False),
        sa.Column('group_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['brd_groups.group_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('group_collaborator_id'),
        sa.UniqueConstraint('group_id', 'user_id', name='uq_group_collaborators_group_user'),
    )
    op.create_index(op.f('ix_group_collaborators_group_id'), 'group_collaborators', ['group_id'], unique=False)
    op.create_index(op.f('ix_group_collaborators_user_id'), 'group_collaborators', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_group_collaborators_user_id'), table_name='group_collaborators')
    op.drop_index(op.f('ix_group_collaborators_group_id'), table_name='group_collaborators')
    op.drop_table('group_collaborators')
