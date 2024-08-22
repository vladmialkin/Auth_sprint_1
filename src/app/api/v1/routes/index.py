from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import insert, select

from app.api.deps import Session
from app.api.v1.schemas.index import IndexSchema
from app.models.index import Index

router = APIRouter()


@router.get("/{id}")
async def get_index(session: Session, id: UUID) -> IndexSchema:
    """
    Получить запись из БД
    """

    query = select(Index).where(Index.id == id)
    return (await session.execute(query)).scalars().first()


@router.post("/")
async def create_index(session: Session, data: IndexSchema) -> IndexSchema:
    """
    Создать запись в БД
    """

    query = insert(Index).values(**data.model_dump()).returning(Index)
    res = (await session.execute(query)).scalars().first()
    await session.commit()

    return res
