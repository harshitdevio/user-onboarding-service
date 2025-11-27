from __future__ import annotations
from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship
)

from app.db.base import Base
from app.db.models.account import Account

from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    # Reverse relationship – a user owns many accounts
    accounts: Mapped[List["Account"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
