"""add revoked tokens

Revision ID: f4b8e1a6c3d9
Revises: a1c9d3f7e2b4
Create Date: 2026-08-10 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4b8e1a6c3d9'
down_revision: Union[str, Sequence[str], None] = 'a1c9d3f7e2b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('revoked_tokens',
    sa.Column('jti', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('jti')
    )
    op.create_index(op.f('ix_revoked_tokens_user_id'), 'revoked_tokens', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_revoked_tokens_user_id'), table_name='revoked_tokens')
    op.drop_table('revoked_tokens')
