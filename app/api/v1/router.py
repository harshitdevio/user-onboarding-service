from fastapi import APIRouter
from . import routes_test, accounts, transactions

router = APIRouter(prefix="/v1")

router.include_router(routes_test.router)
router.include_router(accounts.router)
router.include_router(transactions.router)
