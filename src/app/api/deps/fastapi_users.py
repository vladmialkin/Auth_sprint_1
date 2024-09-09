from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import FastAPIUsers
from fastapi_users.db import SQLAlchemyUserDatabase

from app.api.deps.session import Session
from app.models import User
from app.settings.api import settings as api_settings
from app.settings.jwt import settings as jwt_settings
from app.users.backend import RefreshableAuthenticationBackend
from app.users.manager import UserManager as _UserManager
from app.users.strategy import RefreshableJWTStrategy
from app.users.transport import RefreshableBearerTransport


async def get_user_db(
    session: Session,
) -> AsyncGenerator[SQLAlchemyUserDatabase, None, None]:
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[_UserManager, None, None]:
    yield _UserManager(user_db)


def get_jwt_strategy() -> RefreshableJWTStrategy:
    return RefreshableJWTStrategy(
        secret=api_settings.SECRET_KEY,
        access_lifetime_seconds=jwt_settings.REFRESH_TOKEN_LIFETIME_SECONDS,
        refresh_lifetime_seconds=jwt_settings.REFRESH_TOKEN_LIFETIME_SECONDS,
    )


bearer_transport = RefreshableBearerTransport(tokenUrl="auth/jwt/login")


authentication_backend = RefreshableAuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager, [authentication_backend]
)

UserManager = Annotated[_UserManager, Depends(get_user_manager)]
OAuth2Credentials = Annotated[OAuth2PasswordRequestForm, Depends()]
Strategy = Annotated[
    RefreshableJWTStrategy, Depends(authentication_backend.get_strategy)
]

current_active_user_token = fastapi_users.authenticator.current_user_token(
    active=True
)

current_active_user = fastapi_users.current_user(active=True)


CurrentUserToken = Annotated[tuple, Depends(current_active_user_token)]
CurrentUser = Annotated[tuple, Depends(current_active_user)]
