"""add structured choice data to answers"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b7f2c4d1e8a9"
down_revision: Union[str, Sequence[str], None] = "f4b8e1a6c3d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("answers", sa.Column("choice_data", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("answers", "choice_data")