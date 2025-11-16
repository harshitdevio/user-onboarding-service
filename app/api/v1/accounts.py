from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.schemas import AccountCreate, AccountOut
from app.db.models import Account
from app.db.session import get_db
from uuid import uuid4

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("/", response_model=AccountOut)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    acc = Account(id=uuid4(), currency=payload.currency, balance=0)
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc

@router.get("/", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()
