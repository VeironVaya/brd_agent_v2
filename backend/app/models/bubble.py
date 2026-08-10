from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.utils.ids import new_id


class Bubble(Base):
    __tablename__ = "bubbles"

    bubble_id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    section_id: Mapped[str] = mapped_column(
        ForeignKey("sections.section_id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
