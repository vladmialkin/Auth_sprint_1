from fastapi import APIRouter, HTTPException, status
from fastapi_users.router.common import ErrorCode

from app.api.deps.fastapi_users import (
    CurrentUser,
    CurrentUserToken,
    OAuth2Credentials,
    Strategy,
    UserManager,
    authentication_backend,
    fastapi_users,
)
from app.api.deps.user_agent import UserAgent
from app.api.v1.schemas.user import UserCreateSchema, UserRetrieveSchema

router = APIRouter()


@router.post("/login")
async def login(
    user_agent: UserAgent,
    user_manager: UserManager,
    strategy: Strategy,
    credentials: OAuth2Credentials,
):
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )

    return await authentication_backend.login(
        strategy, user, user_manager, user_agent
    )


@router.post("/logout")
async def logout(
    user_token: CurrentUserToken,
    user_agent: UserAgent,
    strategy: Strategy,
    user_manager: UserManager,
):
    user, token = user_token
    return await authentication_backend.logout(
        strategy, user, user_manager, token, user_agent
    )


@router.post("/refresh")
async def refresh(
    startegy: Strategy,
    refresh_token: ...,
    user_manager: UserManager,
    user_agent: UserAgent,
):
    # return await authentication_backend.refresh(
    #     startegy, user, user_manager, user_agent
    # )
    return {}


router.include_router(
    fastapi_users.get_register_router(UserRetrieveSchema, UserCreateSchema),
)
