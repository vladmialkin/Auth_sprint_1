from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps.fastapi_users import CurrentUser, Session
from app.api.v1.schemas.session import SessionRetrieveSchema
from app.repository.session import session_repository

router = APIRouter()


@router.get("/history/{user_id}")
async def get_history(
    user_token: CurrentUser,
    session: Session,
    user_id: UUID,
) -> list[SessionRetrieveSchema]:
    """Получение истории входов пользователя в аккаунт."""
    user = user_token

    if user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await session_repository.get_history(session)
