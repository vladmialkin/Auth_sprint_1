from pydantic import BaseModel


class JWTTokenRetrieveSchema(BaseModel):
    access_token: str
    refresh_token: str
