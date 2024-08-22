from fastapi import APIRouter

from app.api.v1.routes.index import router as index_router

router = APIRouter(prefix="/api/v1")
router.include_router(prefix="/index", router=index_router, tags=["index"])
