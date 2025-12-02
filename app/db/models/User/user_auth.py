import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class UserAuth(Base):
    __tablename__ = "user_auth"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Security metadata
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)

    password_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))