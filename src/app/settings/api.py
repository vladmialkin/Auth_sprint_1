from app.settings.base import Settings


class ApiSettings(Settings):
    TITLE: str = "auth-api"
    OPENAPI_URL: str = "/api/v1/public/openapi.json"
    DOCS_URL: str = "/api/v1/public/docs"
    REDOC_URL: str = "/api/v1/public/redoc"
    SECRET_KEY: str


settings = ApiSettings()
