from fastapi import Response
from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.types import DependencyCallable
from fastapi_users.authentication.transport import Transport
from fastapi_users.authentication.strategy import Strategy
from app.models import User
from app.users.manager import UserManager
from app.users.schemas import BearerResponseSchema, RefreshResponseSchema
from app.users.strategy import RefreshableJWTStrategy


class RefreshableAuthenticationBackend(AuthenticationBackend):
    # def __init__(
    #     self,
    #     name: str,
    #     transport: Transport,
    #     get_strategy: DependencyCallable[Strategy[models.UP, models.ID]],
    #     get_refresh_strategy: DependencyCallable[Strategy[models.UP, models.ID]]
    # ):
    #     super().__init__(name, transport, get_strategy)
    #     self.get_refresh_strategy = get_refresh_strategy

    async def login(
        self,
        strategy: RefreshableJWTStrategy,
        user: User,
        user_manager: UserManager,
        user_agent: str | None = None,
    ) -> BearerResponseSchema:
        access_token = await strategy.write_access_token(user)
        refresh_token = await strategy.write_refresh_token(user)

        await user_manager.create_session(
            refresh_token, user_agent, user, strategy.refresh_lifetime_seconds
        )

        return BearerResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            # TODO: точно ли нужен token_type?
            token_type="bearer",
        )

    async def refresh(
        self,
        strategy: RefreshableJWTStrategy,
        user: User,
        user_manager: UserManager,
        user_agent: str | None = None,
    ) -> RefreshResponseSchema:
        await user_manager.prolong_session(
            user, user_agent, strategy.refresh_lifetime_seconds
        )

        access_token = await strategy.write_access_token(user)

        return RefreshResponseSchema(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
        )

    async def logout(
        self,
        strategy: RefreshableJWTStrategy,
        user: User,
        user_manager: UserManager,
        token: str,
        user_agent: str | None = None,
    ) -> Response:
        # TODO: возможно стоит перенести в startegy.destroy_token()?
        await user_manager.expire_session(user, user_agent)
        # TODO: добавить токен в blacklist в Redis
        return await super().logout(strategy, user, token)
