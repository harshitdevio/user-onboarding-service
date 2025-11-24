from pydantic import BaseModel, Field
from uuid import UUID


class AccountCreate(BaseModel):
    user_id: UUID
    currency: str = Field(..., example="INR")


class AccountResponse(BaseModel):
    id: UUID
    user_id: UUID
    currency: str
    balance: float
    status: str

    class Config:
        from_attributes = True
