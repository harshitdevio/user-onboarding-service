# import pytest
# from uuid import uuid4

# from jose import jwt
# from httpx import AsyncClient
# from fastapi import status

# from app.db.models.user import User
# from app.core.config import settings

# @pytest.mark.asyncio
# async def test_get_current_user_success(async_db, async_client: AsyncClient):
#     # Create a test user in DB
#     user = User(id=uuid4(), email="x@test.com", hashed_password="xxx")
#     async_db.add(user)
#     await async_db.commit()

#     token = jwt.encode(
#         {"sub": str(user.id)},
#         settings.SECRET_KEY,
#         algorithm=settings.ALGORITHM,
#     )

#     # Hit a protected route that uses get_current_user
#     res = await async_client.get(
#         "/v1/protected-route",
#         headers={"Authorization": f"Bearer {token}"}
#     )

#     assert res.status_code == status.HTTP_200_OK
#     assert res.json()["id"] == str(user.id)
