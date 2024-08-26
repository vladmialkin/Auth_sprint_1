from abc import ABC

from app.models import Session
from .base import BaseRepository


class BaseSessionRepository(ABC, BaseRepository[Session]):
    ...


class SessionRepository(BaseSessionRepository):
    ...
