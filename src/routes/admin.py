from types import NoneType

import cloudinary
import cloudinary.uploader

from datetime import datetime ,date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    status, 
    Path,
    Query
)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter
from src.conf import messages
from src.conf.cloudinary import configure_cloudinary
from src.database.db import get_db
from src.entity.models import User , Avto
from src.repository.users import get_log_info, get_rates_info,get_user_info
from src.repository.admin import get_admin_users_info ,get_number_avto
from src.schemas.user import LogResponse,RateResponse, AvtoResponse, UserResponse
from src.schemas.admin import AdminUserResponse
from src.services.auth import auth_service
from src.repository import users as repository_users
from src.repository import admin as repository_admin
from src.repository import profile as repository_profile

router = APIRouter(prefix="/admin", tags=["admin"])
configure_cloudinary()

@router.get(
    "/users_info",
    response_model=list[AdminUserResponse],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_users_info(
    limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
    ):
    if user.user_type_id not in (2, 3):
            raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    info_users = await get_admin_users_info(limit, offset, user, db)
    if info_users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)

    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param user: User: Specify the type of object that is returned by the auth_service
    :return: The current user, which is stored in the database
    """

    return info_users

@router.get(
    "/search_avto",
    response_model=list[UserResponse],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_current_avto(number: str, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    aboutme = await get_number_avto(number, user, db)
    if aboutme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)

    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param user: User: Specify the type of object that is returned by the auth_service
    :return: The current user, which is stored in the database
    """

    return aboutme


@router.get(
    "/statistics",
    response_model=list[LogResponse],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_current_user(
        all_info: bool,
        number: str | None = None,
        limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user),       
        ):
    log = await get_log_info(all_info, number, limit, offset,user, db)
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.LOG_NOT_FOUND)

    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param user: User: Specify the type of object that is returned by the auth_service
    :return: The current user, which is stored in the database
    """
    return log

