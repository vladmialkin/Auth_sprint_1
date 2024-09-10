from fastapi import APIRouter

from app.api.v1.routes.account import router as account_router
from app.api.v1.routes.auth import router as auth_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router, prefix="/auth/jwt", tags=["Авторизация"])
router.include_router(account_router, prefix="/roles", tags=["Роли"])
