from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.utils.ids import new_id


class Collaborator(Base):
    __tablename__ = "collaborators"
    __table_args__ = (UniqueConstraint("conversation_id", "user_id", name="uq_collaborators_conversation_user"),)

    collaborator_id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.conversation_id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String, nullable=False)  # "editor" | "viewer" — owner is implicit, see erd.md
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
