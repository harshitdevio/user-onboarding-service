import factory
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.User.user_core import User

# Base user factory
class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"  

    # Fixed defaults
    id = factory.LazyFunction(uuid4)
    email = "testuser@example.com"
    hashed_password = "plainpassword123"  
    created_at = factory.LazyFunction(datetime.utcnow)

# Async helper to insert user into test DB
async def create_user(db: AsyncSession, **kwargs) -> User:
    user = UserFactory(**kwargs)
    db.add(user)
    await db.flush()  # flush so SQLAlchemy generates IDs, etc.
    return user