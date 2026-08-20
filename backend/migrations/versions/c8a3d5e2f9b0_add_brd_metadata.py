"""add first-page BRD metadata"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c8a3d5e2f9b0"
down_revision: Union[str, Sequence[str], None] = "b7f2c4d1e8a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("conversations", sa.Column("requestor_directorate", sa.String(), nullable=True))
    op.add_column("conversations", sa.Column("impacted_stakeholders", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("conversations", "impacted_stakeholders")
    op.drop_column("conversations", "requestor_directorate")