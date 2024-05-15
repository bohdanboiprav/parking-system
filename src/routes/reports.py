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
from src.entity.models import User 
from src.repository.reports import get_avto_in_parking, get_reports_scv ,get_statistics
from src.schemas.admin import  IsParkingLog
from src.services.auth import auth_service
from decimal import Decimal
from datetime import time
from fastapi.responses import FileResponse

router = APIRouter(prefix="/reports", tags=["reports"])
configure_cloudinary()

@router.get(
    "/avto in parking",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def avto_in_parking(
    limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
    ):
    """
    Search function on a database of cars in the parking lot.

    :param limit (int): The maximum number of users in the function response.
    :param offset(int): The minimum number of users in the function response.
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A list
    """
    if current_user.user_type_id not in (2, 3):
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    avto_in_parking = await get_avto_in_parking(limit, offset, current_user, db)
    if avto_in_parking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
    return avto_in_parking

@router.get(
    "/download_log",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def download_reports_scv(
    number: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Search function in the database of vehicle entry and exit logs with the ability to download a file scv/

    :param import_csv: bool: File upload condition
    :param number: str: car numb
    :param start_date: date: The minimum number of users in the function response.
    :param end_date: date: Get the connection to the database
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A  list
    """
    if current_user.user_type_id not in (2, 3):
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    reports_scv = await get_reports_scv(number, start_date, end_date, db)
    if reports_scv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.REPORT_NOT_FOUND)
    return FileResponse(path="src/reports/Report.csv", filename='Report.csv',  media_type='multipart/form-data')

@router.get(
    "/statistics",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def download_statistics_scv(
    number: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Search function in the database of vehicle entry and exit logs with the ability to download a file scv/

    :param import_csv: bool: File upload condition
    :param number: str: car numb
    :param start_date: date: The minimum number of users in the function response.
    :param end_date: date: Get the connection to the database
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A users object
    """
    if current_user.user_type_id not in (2, 3):
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    statistics_scv = await get_statistics(number, start_date, end_date, current_user, db)
    if statistics_scv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.STATISTICS_NOT_FOUND_NOT_FOUND)
    return FileResponse(path="src/reports/Statistics.csv", filename='Statistics.csv',  media_type='multipart/form-data')



