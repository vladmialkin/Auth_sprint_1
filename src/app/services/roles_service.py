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


class RolesService:
    def __init__(self, pg_service: PostgresService, auth: AuthJWT):
        self.pg_service = pg_service
        self.auth = auth

    async def create_role(self):
        pass

    async def delete_role(self):
        pass

    async def update_role(self):
        pass

    async def roles_list(self):
        pass

    async def set_role(self):
        pass

    async def revoke_role(self):
        pass

    async def check_user_permissions(self):
        pass


@lru_cache()
def get_roles_service(
        pg_service: PostgresService = Depends(get_postgres_service),
        auth: AuthJWT = Depends(auth_dep)
) -> RolesService:
    return RolesService(pg_service, auth)
