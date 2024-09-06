from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.api.v1.schemas.base import Base


class UserBaseSchema(Base):
    username: Annotated[str, Field(min_length=1, max_length=25)]
    email: Annotated[str, Field(min_length=1, max_length=25)]
    password: Annotated[str, Field(min_length=8, max_length=8)]


class UserCreateSchema(UserBaseSchema): ...


class UserUpdateSchema(UserBaseSchema): ...


class UserRegiserSchema(Base):
    username: Annotated[str, Field(min_length=1, max_length=25)]
    password: Annotated[str, Field(min_length=8, max_length=8)]


class UserLoginSchema(Base):
    username: str
    password: str


class UserRetrieveSchema(Base):
    id: UUID
    username: Annotated[str, Field(min_length=1, max_length=25)]
    email: Annotated[str | None, Field(min_length=1, max_length=25)]
    is_active: bool
    is_stuff: bool
    is_superuser: bool
    last_login: datetime
    created_at: datetime
    updated_at: datetime
