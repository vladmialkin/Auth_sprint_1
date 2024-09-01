from app.settings.base import Settings


class JWTSettings(Settings):
    AUTHJWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int


settings = JWTSettings()
