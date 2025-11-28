from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.transactions import TransactionCreate, TransactionOut
from app.services.transaction_service import create_transaction
from app.db.session import get_db

router = APIRouter(prefix="/transactions",tags=["Transaction"])

@router.post("/", response_model=TransactionOut)
def post_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    tx = create_transaction(db, payload)
    return tx
