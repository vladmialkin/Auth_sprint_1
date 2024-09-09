from fastapi import APIRouter

from app.api.deps.roles import ForAdminOnly

router = APIRouter()


@router.get("/protected_data")
async def protected_data(_: ForAdminOnly):
    return {"data": 42}
