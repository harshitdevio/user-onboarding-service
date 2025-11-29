import factory
from uuid import uuid4
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.account import Account
from app.db.enums import CurrencyCode, AccountStatus
from app.db.models.user import User

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