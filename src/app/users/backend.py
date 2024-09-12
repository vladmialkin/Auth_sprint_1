from fastapi import Response, status, HTTPException
from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.authentication.strategy import JWTStrategy
from fastapi_users.authentication.transport import (
    Transport,
    TransportLogoutNotSupportedError,
)
from fastapi_users.types import DependencyCallable
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Session
from app.users.manager import UserManager
from app.users.schemas import BearerResponseSchema, RefreshResponseSchema
from app.users.strategy import AccessJWTStrategy, RefreshJWTStrategy
from app.repository.session import session_repository


class RefreshableAuthenticationBackend(AuthenticationBackend):
    def __init__(
        self,
        name: str,
        transport: Transport,
        get_access_strategy: DependencyCallable[
            JWTStrategy[models.UP, models.ID]
        ],
        get_refresh_strategy: DependencyCallable[
            JWTStrategy[models.UP, models.ID]
        ],
    ):
        super().__init__(name, transport, get_access_strategy)
        self.get_refresh_strategy = get_refresh_strategy

    async def login(
        self,
        access_strategy: AccessJWTStrategy,
        refresh_strategy: RefreshJWTStrategy,
        user: User,
        db_session: AsyncSession,
        user_agent: str | None = None,
    ) -> BearerResponseSchema:
        access_token = await access_strategy.write_token(user)
        refresh_token = await refresh_strategy.write_token(user)

        await refresh_strategy.create_session(
            refresh_token,
            user_agent,
            user,
            db_session,
        )

        return BearerResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(
        self,
        access_strategy: AccessJWTStrategy,
        refresh_strategy: RefreshJWTStrategy,
        user: User,
        db_session: AsyncSession,
        user_agent: str | None = None,
    ) -> RefreshResponseSchema:
        await refresh_strategy.prolong_session(user, user_agent, db_session)

        access_token = await access_strategy.write_token(user)

        return RefreshResponseSchema(
            access_token=access_token,
        )

    async def logout(
        self,
        access_strategy: AccessJWTStrategy,
        refresh_strategy: RefreshJWTStrategy,
        db_session: AsyncSession,
        token: str,
        user: User,
        user_agent: str | None = None,
    ) -> Response:
        await refresh_strategy.destroy_token(db_session, user, user_agent)
        await access_strategy.destroy_token(token)

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response

    async def get_history(
        self,
        access_strategy: AccessJWTStrategy,
        db_session: AsyncSession,
        token: str,
        user_manager: UserManager,
        user_id: str
    ) -> list[Session]:
        user = await access_strategy.read_token(token, user_manager)

        if any(
                [user is None, not user.is_active, user_id != user.id]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return await session_repository.filter(db_session, user_id=user.id)
