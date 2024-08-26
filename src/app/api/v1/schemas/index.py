import uuid

from app.api.v1.schemas.base import BaseSchema


class IndexSchema(BaseSchema):
    id: uuid.UUID
    message: str
