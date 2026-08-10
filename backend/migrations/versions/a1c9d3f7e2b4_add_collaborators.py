"""add collaborators

Revision ID: a1c9d3f7e2b4
Revises: e35c6ef172c6
Create Date: 2026-08-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c9d3f7e2b4'
down_revision: Union[str, Sequence[str], None] = 'e35c6ef172c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('collaborators',
    sa.Column('collaborator_id', sa.String(), nullable=False),
    sa.Column('conversation_id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.conversation_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('collaborator_id'),
    sa.UniqueConstraint('conversation_id', 'user_id', name='uq_collaborators_conversation_user')
    )
    op.create_index(op.f('ix_collaborators_conversation_id'), 'collaborators', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_collaborators_user_id'), 'collaborators', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_collaborators_user_id'), table_name='collaborators')
    op.drop_index(op.f('ix_collaborators_conversation_id'), table_name='collaborators')
    op.drop_table('collaborators')
