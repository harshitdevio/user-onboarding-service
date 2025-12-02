# app/api/v1/accounts.py
from fastapi import APIRouter, Depends
from typing import Annotated

from app.schemas.account import AccountCreate
from app.services.accounts_service import account_service
from app.db.session import get_db 
from app.db.models.User.user_core import User
from app.auth.dependencies import get_current_user 
from sqlalchemy.orm import Session

router = APIRouter(prefix="/accounts", tags=["accounts"])

async def create_account(
    account_data: AccountCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    account = await account_service.create_account(
        db=db,
        user=current_user,
        payload=account_data
    )
    return account