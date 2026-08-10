from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class SectionDependency(Base):
    __tablename__ = "section_dependencies"

    section_id: Mapped[str] = mapped_column(
        ForeignKey("sections.section_id", ondelete="CASCADE"), primary_key=True
    )
    depends_on_section_id: Mapped[str] = mapped_column(
        ForeignKey("sections.section_id", ondelete="CASCADE"), primary_key=True
    )
