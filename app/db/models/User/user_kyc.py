import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Enum, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from enum import Enum as PyEnum


class KYCStatus(PyEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RESUBMIT = "RESUBMIT"


class UserKYC(Base):
    __tablename__ = "user_kyc"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
    )

    status: Mapped[KYCStatus] = mapped_column(
        Enum(KYCStatus), default=KYCStatus.PENDING, nullable=False
    )

    document_type: Mapped[str|None] = mapped_column(String(50))
    document_number: Mapped[str|None] = mapped_column(String(50))
    document_file_path: Mapped[str|None] = mapped_column(String(255))

    submitted_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True))
    verified_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[str|None] = mapped_column(String(100))
