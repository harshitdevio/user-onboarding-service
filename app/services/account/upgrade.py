from app.repository.account.account import AccountRepository


async def upgrade_account_to_full(*, db, account) -> None:
    repo = AccountRepository()
    await repo.upgrade_to_full(db=db, account_id=account.id)
