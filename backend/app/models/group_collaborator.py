from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.utils.ids import new_id


class GroupCollaborator(Base):
    __tablename__ = "group_collaborators"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_collaborators_group_user"),)

    group_collaborator_id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    group_id: Mapped[str] = mapped_column(
        ForeignKey("brd_groups.group_id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String, nullable=False)  # "editor" | "viewer"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
