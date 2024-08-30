from fastapi import APIRouter
from .routes.users import router as users_router

router = APIRouter(prefix="/api/v1")

router.include_router(prefix="/user", router=users_router, tags=["users"])
