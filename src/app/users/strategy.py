from fastapi_users import exceptions
from fastapi_users.authentication.strategy import JWTStrategy
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from jwt import PyJWTError

from app.models import User
from app.users.manager import UserManager
from app.users.schemas import TokenType


class RefreshableJWTStrategy(JWTStrategy):
    def __init__(
        self,
        secret: SecretType,
        access_lifetime_seconds: int | None = None,
        refresh_lifetime_seconds: int | None = None,
        token_audience: list[str] | None = None,
        algorithm: str = "HS256",
    ):
        if token_audience is None:
            token_audience = ["fastapi-users:auth"]

        super().__init__(
            secret,
            access_lifetime_seconds,
            token_audience,
            algorithm,
        )
        self.refresh_lifetime_seconds = refresh_lifetime_seconds

    async def write_access_token(self, user: User) -> str:
        data = {
            "sub": str(user.id),
            "aud": self.token_audience,
            "token_type": "access",
        }
        return generate_jwt(
            data, self.encode_key, self.lifetime_seconds, self.algorithm
        )

    async def write_refresh_token(self, user: User) -> str:
        data = {
            "sub": str(user.id),
            "aud": self.token_audience,
            "token_type": "refresh",
        }
        return generate_jwt(
            data,
            self.encode_key,
            self.refresh_lifetime_seconds,
            self.algorithm,
        )

    async def read_token(
        self,
        token: str | None,
        user_manager: UserManager,
        token_type: TokenType = "access",
    ) -> User | None:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token,
                self.decode_key,
                self.token_audience,
                algorithms=[self.algorithm],
            )
            user_id = data.get("sub")

            if user_id is None:
                return None

            if data.get("token_type") != token_type:
                return None

        except PyJWTError:
            return None

        # TODO: проверить что токен не в блэклисте
        ...

        try:
            parsed_id = user_manager.parse_id(user_id)
        except exceptions.InvalidID:
            return None

        return await user_manager.get(parsed_id)

    # async def destroy_token(self, token: str, user: Any) -> None:
    #     ...
