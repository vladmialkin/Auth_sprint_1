from abc import ABC

from app.models import RefreshToken
from .base import BaseRepository


class BaseRefreshTokenRepository(ABC, BaseRepository[RefreshToken]):
    ...


class RefreshTokenRepository(BaseRefreshTokenRepository):
    ...
