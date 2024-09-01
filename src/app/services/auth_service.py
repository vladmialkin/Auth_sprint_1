import pprint
from functools import lru_cache
from datetime import datetime, timedelta

from fastapi import Depends, Request
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer

from app.api.v1.schemas.user import TokenSchema
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.schema_validation.user_schema import LoginRequest
from app.settings.jwt import settings
from app.services.postgres_service import PostgresService, get_postgres_service


auth_dep = AuthJWTBearer()


@AuthJWT.load_config
def get_config():
    return settings


class AuthService:
    def __init__(self, pg_service: PostgresService, auth: AuthJWT):
        self.pg_service = pg_service
        self.auth = auth
        self.access_token_expired = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expired = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    async def verify_password(self, plain_password, hashed_password) -> bool:
        """сверяем хеши паролей"""
        return True

    async def create_access_refresh_tokens(self, user_id: str) -> TokenSchema:
        access_token = await self.auth.create_access_token(
            subject=user_id,
            expires_time=self.access_token_expired
        )

        refresh_token = await self.auth.create_refresh_token(
            subject=user_id,
            expires_time=self.refresh_token_expired
        )

        return TokenSchema(access_token=access_token, refresh_token=refresh_token)

    async def login(self, user: LoginRequest, request: Request) -> TokenSchema | bool:
        """
        1. проверяем наличие пользователя по логину в БД. В случае успеха получаем cам объект User
        2. проверяем пароль. В случае успеха получаем True
        3. создаем пару токенов
        4. сохраняем refresh-токен в БД
        5. создаем сессию для пользователя в БД
        """

        # 1 проверяем наличие логина в БД
        db_user = await self.pg_service.get_user_by_login(user.login)  # UserInDB | None
        if not db_user:
            return False

        # 2 проверяем пароль (пока стоит залушка)
        if not await self.verify_password(user.password, db_user.password):
            return False

        # 3 создаем пару токенов
        access_refresh_tokens = await self.create_access_refresh_tokens(str(db_user.id))

        # 4 сохраняем refresh-токен в БД
        token_claim = await self.get_token_claim(access_refresh_tokens.refresh_token)

        await self.pg_service.create_refresh_token(
            token_claim['token_id'],
            token_claim['expired'],
            access_refresh_tokens.refresh_token
        )

        # 5 создаем сессию для пользователя
        user_agent = request.headers.get('user-agent')

        await self.pg_service.create_user_session(db_user.id, user_agent, token_claim['token_id'])

        return access_refresh_tokens

    async def logout(self, user_id: str, request: Request) -> bool:
        """
        1. достаем пользователя по id в БД
        2. устанавливаем is_active=False
        3. сохраняем access_token to Redis с ttl
        4. у refresh_token устанавливаем expiration_date=текущее
        """

        # 1
        db_user = await self.pg_service.get_user_by_id(user_id)
        print(8888, db_user.created_at)
        print(type(db_user.created_at))
        if not db_user:
            return False

        # 2
        await self.pg_service.update(User, user_id, is_active=False)

        # 3 сохраняем access_token to Redis с ttl
        # access_token_header = request.headers.get('authorization')
        # access_token = access_token_header[len('Bearer')+1:]
        # await redis_service.setex(key=user_id, exp_time=10, value=access_token)

        # 4
        await self.pg_service.update_refresh_token(RefreshToken,
                                                   user_id,
                                                   request.headers.get('user-agent'),
                                                   expiration_date=datetime.now())
        return True

    async def refresh(self, user_id, request: Request) -> TokenSchema | bool:
        """
        1. проверяем, что refresh_token not expired
        2. выпускаем новую пару токенов
        3. сохраняем refresh_token в БД
        4. у прежнего refresh_token устанавливаем expiration_date=текущее
        """

        # 1
        token_from_db = await self.pg_service.get_refresh_token(user_id,
                                                                request.headers.get('user-agent'))

        token_from_request = request.headers.get('authorization')[len('Bearer')+1:]

        if not all([
            token_from_request != token_from_db,
            token_from_db.expiration_date > datetime.now()
        ]):
            return False

        # 2
        tokens = await self.create_access_refresh_tokens(user_id)

        # 3
        token_claim = await self.get_token_claim(tokens.refresh_token)

        await self.pg_service.create_refresh_token(
            token_claim['token_id'],
            token_claim['expired'],
            tokens.refresh_token
        )

        # 4
        await self.pg_service.update_refresh_token(RefreshToken,
                                                   user_id,
                                                   request.headers.get('user-agent'),
                                                   expiration_date=datetime.now())

        return tokens

    async def get_history(self, user_id: str, request: Request):
        """
        1. проверяем, что access_token не blacklisted
        2. генерируем историю пользователя
        """
        # 1
        # идем в redis_service

        # 2
        history = await self.pg_service.get_user_sessions(user_id)
        pass

    async def get_token_claim(self, token) -> dict:
        tokens_claims = await self.auth.get_raw_jwt(token)

        token_id = tokens_claims['jti']
        created_at = tokens_claims['iat']
        expired_to_datetime = datetime.fromtimestamp(tokens_claims['exp'])

        return {
            'token_id': token_id,
            'expired': expired_to_datetime
            # 'created_at': created_at, по идее надо брать дату создания токена
        }


@lru_cache()
def get_auth_service(
        pg_service: PostgresService = Depends(get_postgres_service),
        auth: AuthJWT = Depends(auth_dep)
) -> AuthService:
    return AuthService(pg_service, auth)
