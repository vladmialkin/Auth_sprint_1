from typing import Literal
from uuid import UUID

from pydantic import BaseModel

TokenType = Literal["access", "refresh"]


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class BearerResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshResponseSchema(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID
