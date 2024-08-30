import pprint
# from typing import Union
from http import HTTPStatus
from fastapi import APIRouter, Request
from app.api.deps import Session
from sqlalchemy import insert, select

from ..schemas.user import CreateUserSchema, ResponseSchema, ChangeLoginSchema, GetHistorySchema
from app.models.schema_validation.user_schema import CreateUserRequest, ChangeLoginPasswordRequest, LoginRequest, LogoutRequest
from app.models.user import User

router = APIRouter()


# TODO: remove direct work with DB, transfer it to postgres_service.
#  I did it just for an example


@router.post('/register', response_model=CreateUserSchema)
async def create_user(session: Session, data: CreateUserRequest, request: Request) -> CreateUserSchema:
    # 1. get token, data
    # 2. send token into token_service to verify
    # 3. if ok, send data into postgres_service to check if login/email exists
    # 4. if ok, send CreateUserSchema

    print(1111, data)
    headers = request.headers
    query = insert(User).values(**data.model_dump()).returning(User)
    res = (await session.execute(query)).scalars().first()
    await session.commit()
    return res


@router.post('/login', response_model=ResponseSchema)
async def login_user(session: Session, data: LoginRequest) -> ResponseSchema:
    # 1. get session_id, data
    # 2. send session_id into token_service to create a new pair of tokens
    # 3. send data into postgres_service to check if login/email exists
    # 4. if ok, send ResponseSchema, tokens
    print(1111, data)
    login = data.login
    res = ResponseSchema(code=200, message='Success')
    return res


@router.post('/logout', response_model=ResponseSchema)
async def logout_user(session: Session, data: LogoutRequest) -> ResponseSchema:
    # May be we don't need response_model at all and can get data from token (user_id) !!!!!!!!!!
    # 1. get token, data
    # 2. send token into token_service to verify
    # 3. if ok, send data into postgres_service to logout
    # 4. if ok, send ResponseSchema
    print(111, data)
    res = ResponseSchema(code=200, message='Success')
    return res


@router.post('/change_login_password', response_model=ResponseSchema | ChangeLoginSchema)
async def change_login_password(session: Session, data: ChangeLoginPasswordRequest) -> ResponseSchema | ChangeLoginSchema:
    # 1. get token, data
    # 2. send token into token_service to verify
    # 3. if ok, send data into postgres_service to change login, password
    # 4. if ok, send response schema which needed
    print(111, data)
    res = ChangeLoginSchema(login=data.new_login)
    return res


# may be get request instead of post?
@router.post('/get_history', response_model=GetHistorySchema)
async def get_history(session: Session, data: LogoutRequest) -> GetHistorySchema:
    # 1. get token, data
    # 2. send token into token_service to verify
    # 3. if ok, send data into postgres_service to get history info
    # 4. if ok, send GetHistorySchema
    print(111, data)
    res = GetHistorySchema(login=data.login,
                           sessions={'user-agent1': '01-01-2000',
                                     'user-agent2': '01-01-2001'})
    return res


@router.post('/refresh', response_model=ResponseSchema)
async def logout_user(session: Session, data: LogoutRequest) -> ResponseSchema:
    print(111, data)
    res = ResponseSchema(code=200, message='Success')
    return res