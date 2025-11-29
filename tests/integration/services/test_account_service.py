import pytest
from decimal import Decimal

from app.db.models.account import Account
from app.db.enums import CurrencyCode
from app.services.accounts_service import AccountService
from app.schemas.account import AccountCreate

@pytest.mark.asyncio
async def test_create_account_with_inr(async_db, test_user):
    service = AccountService()

    payload = AccountCreate(currency="INR")

    new_acc = await service.create_account(
        db=async_db,
        user=test_user,
        payload=payload
    )

    # BASIC ASSERTIONS
    assert new_acc is not None
    assert new_acc.currency == CurrencyCode.INR     
    assert new_acc.balance == Decimal("0")
    assert new_acc.user_id == test_user.id

    # PERSISTENCE CHECK
    obj_in_db = await async_db.get(Account, new_acc.id)
    assert obj_in_db is not None
    assert obj_in_db.currency == CurrencyCode.INR
    assert obj_in_db.user_id == test_user.id
