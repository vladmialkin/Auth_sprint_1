from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class UserRole(Base):
    __tablename__ = 'user_role'
    user_id: Mapped[UUID] = mapped_column(ForeignKey('auth.user.id', ondelete='CASCADE'), nullable=False)
    role_id: Mapped[UUID] = mapped_column(ForeignKey('auth.role.id', ondelete='CASCADE'), nullable=False)
    UniqueConstraint('user_id', 'role_id')
