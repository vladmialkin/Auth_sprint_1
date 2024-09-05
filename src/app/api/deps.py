from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, status
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgresql import get_async_session
from app.services.session.exceptions import NotAuthenticatedError
from app.settings.api import settings as api_settings
from app.settings.jwt import settings as jwt_settings

Session = Annotated[AsyncSession, Depends(get_async_session)]
UserAgent = Annotated[str | None, Header()]
Token = Annotated[str, Header()]


async def get_current_user_id(access_token: Token) -> UUID:
    try:
        payload = jwt.decode(
            access_token,
            api_settings.SECRET_KEY,
            algorithms=[jwt_settings.ALGORITHM],
        )
    except PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from e

    username: str = payload.get("username")
    user_id: str = payload.get("user_id")

    if not username or not user_id:
        raise NotAuthenticatedError

    return user_id


CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
