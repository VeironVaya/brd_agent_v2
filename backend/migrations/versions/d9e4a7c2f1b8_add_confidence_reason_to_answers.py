"""add confidence_reason and confidence_components to answers"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d9e4a7c2f1b8"
down_revision: Union[str, Sequence[str], None] = "c8a3d5e2f9b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("answers", sa.Column("confidence_reason", sa.String(), nullable=True))
    op.add_column("answers", sa.Column("confidence_components", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("answers", "confidence_components")
    op.drop_column("answers", "confidence_reason")
