import uuid
from abc import abstractmethod, ABC
from typing import Type

from app.models import Role
from .base import BaseRepository


class BaseRoleRepository(ABC, BaseRepository[Role]):

    @abstractmethod
    def get_by_id(self, user_id: uuid.UUID) -> Role:
        ...


class RoleRepository(BaseRoleRepository):
    def get_by_id(self, role_id: uuid.UUID) -> Type[Role] | None:
        return self.session.query(Role).filter(Role.id == role_id).first()
