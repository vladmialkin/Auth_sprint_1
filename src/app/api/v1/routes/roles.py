from typing import Union
from http import HTTPStatus

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.services.roles_service import RolesService, get_roles_service

from ..schemas.user import TokenSchema, CreateUserSchema, ResponseSchema, ChangeLoginSchema, GetHistorySchema, TokenPayload
from app.models.schema_validation.user_schema import CreateUserRequest, ChangeLoginPasswordRequest, LoginRequest


router = APIRouter()


@router.post('/create_role')
async def refresh(
        request: Request,
        roles_service: RolesService = Depends(get_roles_service)
):
    pass


@router.post('/delete_role')
async def refresh(
        request: Request,
        roles_service: RolesService = Depends(get_roles_service)
):
    pass


@router.post('/update_role')
async def refresh(
        request: Request,
        roles_service: RolesService = Depends(get_roles_service)
):
    pass


@router.post('/roles')
async def refresh(
        request: Request,
        roles_service: RolesService = Depends(get_roles_service)
):
    pass


@router.post('/set_role')
async def refresh(
        request: Request,
        roles_service: RolesService = Depends(get_roles_service)
):
    pass


@router.post('/revoke_role')
async def refresh(
        request: Request,
        roles_service: RolesService = Depends(get_roles_service)
):
    pass


@router.post('/check_user_permission')
async def refresh(
        request: Request,
        roles_service: RolesService = Depends(get_roles_service)
):
    pass