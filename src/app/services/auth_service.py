import pprint
from functools import lru_cache
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Request
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from werkzeug.security import generate_password_hash, check_password_hash

from app.api.v1.schemas.user import TokenSchema
from app.models.user import User
from app.models.session import Session
from app.models.refresh_token import RefreshToken
from app.models.user_refresh_token import UserRefreshToken
from app.models.schema_validation.user_schema import LoginRequest, CreateUserRequest
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
        2. проверяем правильность ввода пароля. В случае успеха получаем True
        3. создаем пару токенов
        4. сохраняем refresh-токен в табл RefreshToken
        5. прикрепляем токен к пользователю в табл UserRefreshToken
        6. создаем сессию для пользователя в БД
        """

        # 1 проверяем наличие логина в БД
        db_user = await self.pg_service.get_user_by_field(user_login=user.login)  # UserInDB | None
        if not db_user:
            return False

        # 2 проверяем правильность ввода пароля
        if not check_password_hash(db_user.password, user.password):
            return False

        # 3 создаем пару токенов
        tokens = await self.create_access_refresh_tokens(str(db_user.id))

        # 4 сохраняем refresh-токен в БД
        refresh_token_payload = await self.get_token_claim(tokens.refresh_token)

        db_refresh_token = await self.pg_service.create(
            RefreshToken,
            token=tokens.refresh_token,
            expiration_date=refresh_token_payload['expired']
        )

        # 5 прикрепляем токен к пользователю
        await self.pg_service.create(UserRefreshToken, user_id=db_user.id, refresh_token_id=db_refresh_token.id)

        # 6 создаем сессию для пользователя
        user_agent = request.headers.get('user-agent')
        await self.pg_service.create(Session, user_id=db_user.id, user_agent=user_agent)

        return tokens

    async def logout(self, user_id: str, request: Request) -> bool:
        """
        1. достаем пользователя по id в БД
        2. устанавливаем is_active=False
        3. сохраняем access_token to Redis с ttl
        4. у refresh_token устанавливаем expiration_date=текущее
        """

        # 1 достаем пользователя по id в БД
        db_user = await self.pg_service.get_user_by_field(user_id=user_id)
        if not db_user:
            return False

        # 2 устанавливаем is_active=False
        await self.pg_service.update(User, user_id, is_active=False)

        # 3 сохраняем access_token to Redis с ttl
        # access_token_header = request.headers.get('authorization')
        # access_token = access_token_header[len('Bearer')+1:]
        # await redis_service.setex(key=user_id, exp_time=10, value=access_token)

        # 4 устанавливаем is_active=False
        # refresh_token_id = await self.pg_service.get_refresh_token_id(db_user.id, user_agent)
        #
        # await self.pg_service.update(RefreshToken, user_id, expiration_date=datetime.now())
        return True

    async def refresh(self, user_id_from_request, request: Request) -> TokenSchema | bool:
        """
        1. проверяем в табл RerfeshToken что refresh_token существует и not expired
        2. проверяем в табл UserRefreshToken, что токен принадлежит пользователю, который отправил запрос
        3. выпускаем новую пару токенов
        4. сохраняем refresh_token в табл RerfeshToken
        5. прикрепляем токен к пользователю в табл UserRefreshToken
        4. у старого refresh_token устанавливаем expiration_date=текущее
        """

        # 1 проверяем в табл RerfeshToken, что refresh_token существует и not expired
        token_from_request = request.headers.get('authorization')[len('Bearer')+1:]
        db_old_token = await self.pg_service.get_token_by_token(token_from_request)

        if any([
            db_old_token is None,
            db_old_token.expiration_date < datetime.now(timezone.utc).replace(microsecond=0)
        ]):
            return False

        # 2 проверяем в табл UserRefreshToken, что токен принадлежит пользователю, который отправил запрос
        db_user_id = await self.pg_service.get_userid_by_tokenid(db_old_token.id)
        if user_id_from_request != str(db_user_id.user_id):
            return False

        # 3 выпускаем новую пару токенов
        new_tokens = await self.create_access_refresh_tokens(user_id_from_request)

        # 4 сохраняем refresh_token в табл RerfeshToken
        token_claim = await self.get_token_claim(new_tokens.refresh_token)

        db_new_token = await self.pg_service.create(
            RefreshToken,
            token=new_tokens.refresh_token,
            expiration_date=token_claim['expired']
        )

        # 5 прикрепляем токен к пользователю в табл UserRefreshToken
        await self.pg_service.create(
            UserRefreshToken,
            user_id=user_id_from_request,
            refresh_token_id=db_new_token.id
        )

        # 6
        db_old_token.expiration_date = datetime.now()
        await self.pg_service.update(RefreshToken, db_old_token.id, expiration_date=datetime.now())

        return new_tokens

    async def register(self, user: CreateUserRequest, request: Request) -> TokenSchema | bool:
        """
        1. создаем пользователя. проверка наличия пользователя по логину и email в БД происходит на уровне БД.
        2. создаем пару токенов
        3. сохраняем refresh_token в табл RerfeshToken
        4. прикрепляем токен к пользователю в табл UserRefreshToken
        5. создаем сессию для пользователя в БД
        """

        # 1 создаем пользователя
        user.password = generate_password_hash(user.password)

        new_user = await self.pg_service.create_user(user)
        if not new_user:
            return False

        # 2 создаем пару токенов
        new_tokens = await self.create_access_refresh_tokens(str(new_user.id))

        # 3 сохраняем refresh_token в табл RerfeshToken
        token_claim = await self.get_token_claim(new_tokens.refresh_token)

        db_refresh_token = await self.pg_service.create(
            RefreshToken,
            expiration_date=token_claim['expired'],
            token=new_tokens.refresh_token
        )

        # 4 прикрепляем токен к пользователю в табл UserRefreshToken
        await self.pg_service.create(
            UserRefreshToken,
            user_id=new_user.id,
            refresh_token_id=db_refresh_token.id
        )

        # 5 создаем сессию для пользователя в БД
        user_agent = request.headers.get('user-agent')
        await self.pg_service.create(Session, user_id=new_user.id, user_agent=user_agent)

        return new_tokens

    async def get_history(self, user_id: str, request: Request):
        """
        1. проверяем, что access_token не blacklisted
        2. генерируем историю пользователя
        """
        # 1
        # идем в redis_service

        # 2
        session_info = await self.pg_service.get_session_info(Session, user_id)
        pass

    async def change_login_password(self, user_id, request: Request):
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
