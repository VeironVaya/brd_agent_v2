from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.utils.ids import new_id


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    context: Mapped[str | None] = mapped_column(String, nullable=True)
    requestor_directorate: Mapped[str | None] = mapped_column(String, nullable=True)
    impacted_stakeholders: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_generated_version: Mapped[str | None] = mapped_column(String, nullable=True)
    # Which leaf's Room the frontend is currently showing ("Currently discussing: X").
    # Not in erd.md's original attribute table — added here since api_contract.md's
    # GET /conversations/:id has always returned focused_field_id and nothing else
    # backs it. Set by ChatService whenever a message is posted to a room.
    focused_section_id: Mapped[str | None] = mapped_column(
        ForeignKey("sections.section_id", ondelete="SET NULL"), nullable=True
    )
    # Which group this BRD belongs to. NULL means ungrouped.
    group_id: Mapped[str | None] = mapped_column(
        ForeignKey("brd_groups.group_id", ondelete="SET NULL"), nullable=True, index=True
    )
