from typing import Union
from http import HTTPStatus

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.api.deps import Session
from sqlalchemy import insert, select
from async_fastapi_jwt_auth.exceptions import MissingTokenError, JWTDecodeError, AccessTokenRequired
from app.services.user_service import UserService, get_user_service

from ..schemas.user import TokenSchema, CreateUserSchema, ResponseSchema, ChangeLoginSchema, GetHistorySchema, TokenPayload
from app.models.schema_validation.user_schema import CreateUserRequest, ChangeLoginPasswordRequest, LoginRequest, LogoutRequest
from app.models.user import User


router = APIRouter()


# TODO: remove direct work with DB, transfer it to postgres_service.
#  I did it just for an example

@router.post('/login', response_model=TokenSchema)
async def login_user(user: LoginRequest, request: Request, user_service: UserService = Depends(get_user_service)) -> TokenSchema:
    tokens = await user_service.authenticate_by_login_pwd(user, request)

    if not tokens:
        exp_msg = f"Неверное имя пользователя или пароль"
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=exp_msg)

    return TokenSchema(
        access_token=tokens['access_token'],
        refresh_token=tokens['refresh_token']
    )


@router.post('/register', response_model=CreateUserSchema)
async def create_user(session: Session, data: CreateUserRequest, request: Request) -> CreateUserSchema:
    print(1111, data)
    headers = request.headers
    print(2222, headers)

    query = insert(User).values(**data.model_dump()).returning(User)
    res = (await session.execute(query)).scalars().first()
    await session.commit()
    return res


@router.post('/logout', response_model=ResponseSchema)
async def logout_user(data: LogoutRequest) -> ResponseSchema:
    print(111, data)
    res = ResponseSchema(code=200, message='Success')
    return res


@router.post('/change_login_password', response_model=Union[ResponseSchema, ChangeLoginSchema])
async def change_login_password(data: ChangeLoginPasswordRequest) -> Union[ResponseSchema, ChangeLoginSchema]:
    print(111, data)
    res = ChangeLoginSchema(login=data.new_login)
    return res


@router.get('/get_history', response_model=GetHistorySchema)
async def get_history(user_service: UserService = Depends(get_user_service)) -> GetHistorySchema:
    try:
        await user_service.auth.jwt_required()
    except MissingTokenError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except JWTDecodeError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except AccessTokenRequired as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    user_id = await user_service.auth.get_jwt_subject()
    user_history = await user_service.get_history(user_id)

    print(22222, user_id)
    res = GetHistorySchema(login='sf',
                           sessions={'user-agent1': '01-01-2000',
                                     'user-agent2': '01-01-2001'})
    return res


@router.post('/refresh', response_model=ResponseSchema)
async def logout_user(session: Session, data: LogoutRequest) -> ResponseSchema:
    print(111, data)
    res = ResponseSchema(code=200, message='Success')
    return res