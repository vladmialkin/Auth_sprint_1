from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.repository.session import session_repository
from app.api.v1.schemas.session import UserHistoryRetrieveSchema
from app.api.deps.fastapi_users import (
    AccessStrategy,
    CurrentUserToken,
    Session,
    UserManager,
    authentication_backend
)

router = APIRouter()


@router.get("/history/{user_id}")
async def get_history(
    user_token: CurrentUserToken,
    access_strategy: AccessStrategy,
    session: Session,
    user_manager: UserManager,
    user_id: UUID
) -> list[UserHistoryRetrieveSchema]:
    """Получение истории входов пользователя в аккаунт."""
    user, token = user_token
    user = await access_strategy.read_token(token, user_manager)

    if user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return await session_repository.get_history(
        session,
        user_id=user.id
    )
