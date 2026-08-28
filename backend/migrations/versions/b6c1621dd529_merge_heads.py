"""merge_heads

Revision ID: b6c1621dd529
Revises: d9e4a7c2f1b8, i3j4k5l6m7n8
Create Date: 2026-08-27 21:07:23.359770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6c1621dd529'
down_revision: Union[str, Sequence[str], None] = ('d9e4a7c2f1b8', 'i3j4k5l6m7n8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
