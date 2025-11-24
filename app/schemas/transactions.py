from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from typing import Optional
from app.db.models import TransactionStatus, CurrencyCode

class TransactionCreate(BaseModel):
    idempotency_key: str
    sender_account: UUID
    receiver_account: UUID
    amount: Decimal
    currency: CurrencyCode
    additional_metadata: Optional[dict] = None


class TransactionOut(BaseModel):
    id: UUID
    status: TransactionStatus
    amount: Decimal
    currency: CurrencyCode

    class Config:
        orm_mode = True
