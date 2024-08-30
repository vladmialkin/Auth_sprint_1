import datetime

from pydantic import Field

from ..schemas.base import BaseSchema


class ResponseSchema(BaseSchema):
    code: int = Field(title='Status_code', description='Коды состояния HTTP-ответа')
    message: str = Field(title='Сообщение')


class CreateUserSchema(BaseSchema):
    login: str = Field(description="Логин пользователя")
    email: str = Field(description="Электронная почта пользователя")
    created_at: datetime.datetime = Field(description="Дата создания аккаунта")


class ChangeLoginSchema(BaseSchema):
    new_login: str = Field(description="Новый логин пользователя")


class GetHistorySchema(BaseSchema):
    login: str = Field(description="Логин пользователя")
    sessions: dict = Field(description="История входов в аккаунт")


class TokenSchema(BaseSchema):
    access_token: str
    refresh_token: str



