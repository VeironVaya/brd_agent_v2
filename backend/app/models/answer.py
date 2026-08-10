from datetime import datetime

from sqlalchemy import ARRAY, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Answer(Base):
    __tablename__ = "answers"

    section_id: Mapped[str] = mapped_column(
        ForeignKey("sections.section_id", ondelete="CASCADE"), primary_key=True
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="ready")
    completeness: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    answer_text: Mapped[str | None] = mapped_column(String, nullable=True)
    missing_items: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
