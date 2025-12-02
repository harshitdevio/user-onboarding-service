import factory
from uuid import uuid4
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.account import Account
from app.db.enums import CurrencyCode, AccountStatus
from app.db.models.User.user_core import User

class AccountFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Account
        sqlalchemy_session_persistence = "flush"  
    # Fixed defaults
    id = factory.LazyFunction(uuid4)
    currency = CurrencyCode.INR
    balance = Decimal("0.0")
    status = AccountStatus.ACTIVE
    created_at = factory.LazyFunction(datetime.utcnow)

    user_id = None  


# 2. Async helper to insert account into test DB
async def create_account(db: AsyncSession, user: User, **kwargs) -> Account:
    if "user_id" not in kwargs:
        kwargs["user_id"] = user.id

    account = AccountFactory(**kwargs)
    db.add(account)
    await db.flush()  # flush so SQLAlchemy generates IDs
    return account