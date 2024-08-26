from abc import abstractmethod, ABC

from app.models import UserRole
from app.repositories.base import BaseRepository


class BaseUserRoleRepository(ABC, BaseRepository[UserRole]):

    @abstractmethod
    def get_by_id(self):
        ...


class UserRoleRepository(BaseUserRoleRepository):
    def get_by_id(self):
        ...
