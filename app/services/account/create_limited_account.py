from app.repository.account.account import AccountRepository
from app.domain.risks.evaluate import RiskDecision


class RiskNotApproved(Exception):
    pass


async def create_limited_account(
    *,
    db,
    user,
) -> None:
    """
    Create a LIMITED account for approved users only.
    """

    if user.risk_decision != RiskDecision.ALLOW:
        raise RiskNotApproved()

    repo = AccountRepository()

    await repo.create_limited(
        db=db,
        user_id=user.id,
        daily_limit=10_000,  
    )
