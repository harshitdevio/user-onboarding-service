# app/api/v1/accounts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from uuid import uuid4
from decimal import Decimal
from typing import Annotated

from app.schemas.account import AccountCreate, AccountResponse 
from app.db.session import get_db 
from app.db.models.account import Account, User
from app.auth.dependencies import get_current_user 
from app.services.audit_log import create_audit_log
from app.db.enums import CurrencyCode
from sqlalchemy.orm import Session

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post(
    "/",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
    description="Creates a new account for the authenticated user with the specified currency"
)
async def create_account(
    account_data: AccountCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    
    if account_data.currency.upper() not in CurrencyCode.__members__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported currency. Supported: {', '.join(CurrencyCode)}"
        )
    
    try:
        existing_account = db.execute(
            select(Account).where(
                Account.user_id == current_user.id,
                Account.currency == account_data.currency.upper()
            )
        ).scalar_one_or_none()
        
        if existing_account:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User already has a {account_data.currency.upper()} account"
            )
        
        # Create new account
        new_account = Account(
            id=uuid4(), # ID of the account (PK)
            user_id=current_user.id, #ID of the owner of the Account (FK)
            currency=account_data.currency.upper(),
            balance=Decimal("0.000000"),  # Start with zero balance
            status="ACTIVE"
        )
        
        db.add(new_account)
        
        # Create audit log entry
        audit_entry = create_audit_log(
    db,
    actor=str(current_user.id),
    action="CREATE_ACCOUNT",
    object_type="ACCOUNT",
    object_id=new_account.id,
    payload={
        "user_id": str(current_user.id),
        "currency": new_account.currency,
        "initial_balance": "0.00"
    }
)

        db.add(audit_entry)
        db.commit()
        db.refresh(new_account)

        # API's response after successfully creating the account & the audit log.
        return AccountResponse(
            id=new_account.id,
            user_id=new_account.user_id,
            currency=new_account.currency,
            balance=float(new_account.balance),
            status=new_account.status
        )
    
    # Handles error if either Account or AuditLog creation fails!    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database integrity error occurred"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

