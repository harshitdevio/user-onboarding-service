import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), unique=True, index=True
    )
    full_name: Mapped[str | None] = mapped_column(String(100))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_frozen: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    accounts: Mapped[list["Account"]] = relationship(        # pyright: ignore
        "Account",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    auth: Mapped["UserAuth"] = relationship(                 # pyright: ignore
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    kyc: Mapped["UserKYC"] = relationship(                  # pyright: ignore
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )