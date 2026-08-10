from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class RevokedToken(Base):
    """A JWT `jti` that was explicitly logged out before its own `exp`.
    Row is meaningless once `expires_at` passes — the token would fail
    signature verification's own exp check by then regardless — but rows
    are cheap and small-scale enough here that pruning isn't worth the
    added machinery yet."""

    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
