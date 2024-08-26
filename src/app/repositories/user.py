import uuid
from abc import abstractmethod, ABC
from app.models import User

from app.repositories.base import BaseRepository


class BaseUserRepository(ABC, BaseRepository[User]):

    @abstractmethod
    def get_by_id(self, user_id: uuid.UUID) -> User:
        ...


class UserRepository(BaseUserRepository):
    def get_by_id(self, user_id: uuid.UUID) -> User:
        ...
