from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps.fastapi_users import CurrentUser, Session
from app.api.v1.schemas.session import SessionRetrieveSchema
from app.repository.session import session_repository

router = APIRouter()


@router.get("/history")
async def get_history(
    user_token: CurrentUser,
    session: Session
) -> list[SessionRetrieveSchema]:
    """Получение истории входов пользователя в аккаунт."""
    user = user_token
    return await session_repository.get_history(session, user.id)
