from app.settings.base import Settings


class CryptContextSettings(Settings):
    SCHEMES: list[str] = ["pbkdf2_sha256"]
    DEPRECATED: str = "auto"


settings = CryptContextSettings()
