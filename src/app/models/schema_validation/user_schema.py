from pydantic import BaseModel, Field
from uuid import UUID


class UserInDB(BaseModel):
    """What we get from Postgres"""
    id: UUID = Field(description="Идентификатор пользователя")
    login: str = Field(description="Логин пользователя")
    password: str = Field(description="Пароль пользователя")
    email: str = Field(description="Электронная почта пользователя")
    created_at: str = Field(description="Дата создания аккаунта")
    is_active: bool = Field(description="Находится ли пользователь онлайн")
    is_stuff: bool = Field(description="Является ли пользователь сотрудником")
    is_super_user: bool = Field(description="Является ли пользователь суперпользователем")
    updated_at: str = Field(description="Дата дата обновления данных пользователя")
    salt: bytes = Field(description="Соль для пароля пользователя")


class CreateUserRequest(BaseModel):
    login: str = Field(description="Логин пользователя")
    password: str = Field(description="Пароль пользователя")
    email: str = Field(description="Электронная почта пользователя")


class LoginRequest(BaseModel):
    login: str = Field(description="Логин пользователя")
    password: str = Field(description="Пароль пользователя")


class LogoutRequest(BaseModel):
    login: str = Field(description="Логин пользователя")


class ChangeLoginPasswordRequest(BaseModel):
    old_login: str | None = Field(None, description="Старый логин пользователя")
    new_login: str | None = Field(None, description="Новый логин пользователя")
    old_password: str | None = Field(None, description="Старый пароль пользователя")
    new_password: str | None = Field(None, description="Новый пароль пользователя")


class GetHistoryRequest(BaseModel):
    login: str = Field(description="Логин пользователя")


