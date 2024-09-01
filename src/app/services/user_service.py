import pprint
from functools import lru_cache
from datetime import datetime, timedelta

from fastapi import Depends, Request
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer

from app.models.schema_validation.user_schema import LoginRequest
from app.settings.jwt import settings
from app.services.postgres_service import PostgresService, get_postgres_service


auth_dep = AuthJWTBearer()


@AuthJWT.load_config
def get_config():
    return settings


class UserService:
    def __init__(self, pg_service: PostgresService, auth: AuthJWT):
        self.pg_service = pg_service
        self.auth = auth

    async def verify_password(self, plain_password, hashed_password) -> bool:
        """сверяем хеши паролей"""
        return True

    async def verify_login(self):
        pass

    async def authenticate_by_login_pwd(self, user: LoginRequest, request: Request) -> dict | bool:
        # 1. проверяем наличие логина в БД. В случае успеха получаем cам объект User
        # 2. проверяем пароль. В случае успеха получаем True
        # 3. создаем пару токенов
        # 4. сохраняем refresh-токен в БД
        # 5. создаем сессию для пользователя в БД

        # 1 проверяем наличие логина в БД
        db_user = await self.pg_service.get_user_by_login(user.login)  # UserInDB | None
        if not db_user:
            return False

        # 2 проверяем пароль (пока стоит залушка)
        if not await self.verify_password(user.password, db_user.password):
            return False

        # 3 создаем пару токенов
        access_token_exp = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await self.auth.create_access_token(
            subject=str(db_user.id),
            expires_time=access_token_exp
        )

        refresh_token_exp = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_token = await self.auth.create_refresh_token(
            subject=str(db_user.id),
            expires_time=refresh_token_exp
        )

        # 4 сохраняем refresh-токен в БД
        token_claim = await self.get_token_claim(refresh_token)

        await self.pg_service.create_refresh_token(
            token_claim['token_id'],
            token_claim['expired'],
            refresh_token
        )

        pprint.pprint(token_claim)

        # 5 создаем сессию для пользователя
        user_agent = request.headers.get('user-agent')
        print(2222, user_agent)

        await self.pg_service.create_user_session(db_user.id, user_agent, token_claim['token_id'])

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    async def get_history(self, user_id: str):
        history = await self.pg_service.get_user_sessions(user_id)
        pass

    async def get_token_claim(self, token) -> dict:
        tokens_claims = await self.auth.get_raw_jwt(token)
        token_id = tokens_claims['jti']
        created_at = tokens_claims['iat']
        expired_int = tokens_claims['exp']
        expired_to_datetime = datetime.fromtimestamp(expired_int)

        return {
            'token_id': token_id,
            'expired': expired_to_datetime
            # 'created_at': created_at, по идее надо брать дату создания токена
        }


@lru_cache()
def get_user_service(
        pg_service: PostgresService = Depends(get_postgres_service),
        auth: AuthJWT = Depends(auth_dep)
) -> UserService:
    return UserService(pg_service, auth)
