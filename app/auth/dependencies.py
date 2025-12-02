from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from jose import jwt, JWTError

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.db.models.User.user_core import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception

        user_uuid = UUID(user_id)

    except (JWTError, ValueError):
        # JWT invalid OR UUID parse failed
        raise credentials_exception

    # Fast primary-key fetch
    user = await db.get(User, user_uuid)
    if user is None:
        raise credentials_exception

    return user

