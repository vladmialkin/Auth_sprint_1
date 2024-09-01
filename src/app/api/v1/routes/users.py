from typing import Union
from http import HTTPStatus

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.api.deps import Session
from sqlalchemy import insert, select
from async_fastapi_jwt_auth.exceptions import MissingTokenError, JWTDecodeError, AccessTokenRequired, RefreshTokenRequired
from app.services.auth_service import AuthService, get_auth_service

from ..schemas.user import TokenSchema, CreateUserSchema, ResponseSchema, ChangeLoginSchema, GetHistorySchema, TokenPayload
from app.models.schema_validation.user_schema import CreateUserRequest, ChangeLoginPasswordRequest, LoginRequest
from app.models.user import User


router = APIRouter()


@router.post('/refresh', response_model=TokenSchema)
async def refresh(
        request: Request,
        auth_service: AuthService = Depends(get_auth_service)
) -> TokenSchema:
    try:
        await auth_service.auth.jwt_refresh_token_required()
    except MissingTokenError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except RefreshTokenRequired as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except JWTDecodeError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    current_user_id = await auth_service.auth.get_jwt_subject()
    new_tokens = await auth_service.refresh(current_user_id, request)

    if not new_tokens:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail='Токен не валиден')

    return new_tokens


@router.post('/login', response_model=TokenSchema)
async def login_user(
        user: LoginRequest,
        request: Request,
        auth_service: AuthService = Depends(get_auth_service)
) -> TokenSchema:
    tokens = await auth_service.login(user, request)

    if not tokens:
        exp_msg = f"Неверное имя пользователя или пароль"
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=exp_msg)

    return tokens


@router.post('/logout', response_model=ResponseSchema)
async def logout_user(request: Request, auth_service: AuthService = Depends(get_auth_service)) -> ResponseSchema:
    try:
        await auth_service.auth.jwt_required()
    except MissingTokenError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except JWTDecodeError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except AccessTokenRequired as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    user_id = await auth_service.auth.get_jwt_subject()

    res = await auth_service.logout(user_id, request)
    if not res:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Пользователь не авторизован')

    return ResponseSchema(code=HTTPStatus.OK, message='Пользователь вышел из аккаунта')


@router.post('/register', response_model=CreateUserSchema)
async def create_user(session: Session, data: CreateUserRequest, request: Request) -> CreateUserSchema:
    print(1111, data)
    headers = request.headers
    print(2222, headers)

    query = insert(User).values(**data.model_dump()).returning(User)
    res = (await session.execute(query)).scalars().first()
    await session.commit()
    return res


@router.post('/change_login_password', response_model=Union[ResponseSchema, ChangeLoginSchema])
async def change_login_password(data: ChangeLoginPasswordRequest) -> Union[ResponseSchema, ChangeLoginSchema]:
    print(111, data)
    res = ChangeLoginSchema(login=data.new_login)
    return res


@router.get('/get_history', response_model=GetHistorySchema)
async def get_history(
        request: Request,
        auth_service: AuthService = Depends(get_auth_service)
) -> GetHistorySchema:
    try:
        await auth_service.auth.jwt_required()
    except MissingTokenError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except JWTDecodeError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except AccessTokenRequired as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

    user_id = await auth_service.auth.get_jwt_subject()

    user_history = await auth_service.get_history(user_id, request)

    if not user_history:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='History not found')

    # TODO: наверно нужно кодировать данные?
    res = GetHistorySchema(login='sf',
                           sessions={'user-agent1': '01-01-2000',
                                     'user-agent2': '01-01-2001'})
    return res
