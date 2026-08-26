"""add performance indexes

Revision ID: d1e2f3a4b5c6
Revises: c8a3d5e2f9b0
Create Date: 2026-08-20 08:30:00.000000

Indexes added:
- bubbles(section_id, created_at) -- ORDER BY created_at queries per section
- revoked_tokens(expires_at)      -- startup cleanup scan
- conversations(updated_at)       -- ORDER BY for list endpoints
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = "c8a3d5e2f9b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes on hot query paths."""
    # Bubble queries always ORDER BY created_at within a section.
    op.create_index(
        "ix_bubbles_section_id_created_at",
        "bubbles",
        ["section_id", "created_at"],
        unique=False,
    )
    # Startup cleanup DELETE scans on expires_at.
    op.create_index(
        "ix_revoked_tokens_expires_at",
        "revoked_tokens",
        ["expires_at"],
        unique=False,
    )
    # List endpoints sort conversations by updated_at.
    op.create_index(
        "ix_conversations_updated_at",
        "conversations",
        ["updated_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index("ix_conversations_updated_at", table_name="conversations")
    op.drop_index("ix_revoked_tokens_expires_at", table_name="revoked_tokens")
    op.drop_index("ix_bubbles_section_id_created_at", table_name="bubbles")
