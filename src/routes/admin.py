from types import NoneType

import cloudinary
import cloudinary.uploader

from datetime import datetime , date, time

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
from sqlalchemy import select, func , create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter
from src.conf import messages
from src.conf.cloudinary import configure_cloudinary
from src.database.db import get_db
from src.entity.models import User , Avto
from src.repository.users import get_log_info, get_rates_info,get_user_info
from src.repository.admin import get_admin_users_info ,get_number_avto, get_ban_avto
from src.schemas.user import LogResponse,RateResponse, AvtoResponse, UserResponse, RateTimeResponse
from src.schemas.admin import AdminUserResponse, AdminAvtoResponse
from src.services.auth import auth_service
from src.repository import users as repository_users
from src.repository import admin as repository_admin
from src.repository import profile as repository_profile
from decimal import Decimal

router = APIRouter(prefix="/admin", tags=["admin"])
configure_cloudinary()

@router.put("/replenishment_of_balans", 
            dependencies=[Depends(RateLimiter(times=1, seconds=2))],
            status_code=status.HTTP_200_OK)
async def replenishment_of_balans(
    email: str ,
    replenishment: Decimal | None = None ,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
     ):
    """
    The replenishment_of_balags function updates a user's balance.
        Args:
            - email(str): str object containing the user's email
            - replenishment (Decimal): User's account top-up amount
            - db (AsyncSession, optional): [description]. Defaults to Depends(get_db).
            - current_user (User, optional): [description]. Defaults to Depends(auth_service.get_current_user).

    :param email: str: User`s email
    :param replenishment: Decimal: Get the connection to the database
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A user object
    """
    if current_user.user_type_id not in (2, 3):
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    user = await repository_admin.update_balans(email, replenishment, db, current_user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
    return user

@router.get(
    "/users_info",
    response_model=list[AdminUserResponse],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_users_info(
    email: str | None = None,
    limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    """
    The function get_users_info receives the input mail or None if the input is None,
       and returns information about all users if the mail returns information about the user of this mail.
             Args:
                - email(str): str object containing the user's email
                - limit (int): The maximum number of users in the function response.
                - offset(int): The minimum number of users in the function response.
                - db (AsyncSession, optional): [description]. Defaults to Depends(get_db).
                - current_user (User, optional): [description]. Defaults to Depends(auth_service.get_current_user)
                - :return: A user object
    
    :param email: str: User`s email
    :param limit (int): The maximum number of users in the function response.
    :param offset(int): The minimum number of users in the function response.
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A users object
    """
    info_users = await get_admin_users_info(email, limit, offset, current_user, db)
    if info_users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
    return info_users

@router.get(
    "/search_avto",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def search_number_avto(number: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):

    """
    The get_current_avto function for searching information about 
        a car by number. Receives the car number as input.
    
    :param number: str: User`s number avto
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A users object
    """
    if current_user.user_type_id not in (2, 3):
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)    
    info_avto = await get_number_avto(number, db)
    if info_avto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.AVTO_NOT_FOUND)
    return info_avto

@router.put("/ban_avto", response_model=AdminAvtoResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=2))],
            status_code=status.HTTP_200_OK)
async def ban_avto(
    ban_avto: bool,
    number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
     ):
    """
    Function ban_avto for blocking a car in the database. Takes the car number as input
        Args:
            - ban_avto (bool): Boolean value true or false, true to block, false to unlock.
            - db (AsyncSession, optional): [description]. Defaults to Depends(get_db).
            - current_user (User, optional): [description]. Defaults to Depends(auth_service.get_current_user).

    :param ban_avto: Boolean value
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A user object
    """
    if current_user.user_type_id not in (2, 3):
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION) 
    avto = await repository_admin.ban_avto(ban_avto, number, db, current_user)
    if avto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.AVTO_NOT_FOUND)
    return avto

@router.delete("/remove_avto",  status_code=status.HTTP_200_OK)
async def remove_avto(number: str,\
    db: AsyncSession = Depends(get_db),\
    current_user: User = Depends(auth_service.get_current_user)):
    """
    Function remove_avto for delete a car with the database.

    :param number: Number avto
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A user object
    """
    if current_user.user_type_id not in (2, 3):
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION) 
    avto = await repository_admin.remove_avto(number, db, current_user)
    if avto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.AVTO_NOT_FOUND)
    return { "detail": "Avto deleted successfully"}


@router.get(
    "/info_ban_avto",
    response_model=list[AvtoResponse],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def info_ban_avto(
    limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    """   
    Search info_ban_avto function for blocked cars in the database.

    :param limit (int): The maximum number of users in the function response.
    :param offset(int): The minimum number of users in the function response.
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A avto object
    """
    if current_user.user_type_id not in (2, 3):
            raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    ban_avto = await get_ban_avto(limit, offset, current_user, db)
    if ban_avto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.AVTO_NOT_FOUND)
    if current_user.user_type_id not in (2, 3):
            raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    ban_avto = await get_ban_avto(limit, offset, current_user, db)
    if ban_avto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.AVTO_NOT_FOUND)
    return ban_avto

@router.post("/create_rate", response_model=RateResponse)
async def create_rate(
        rate_name: str ,
        price: Decimal ,
        pricetime: int ,
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)):  
    """
    The create_rate function creates a new rate in the database.
        It takes in a ratename str,a price Decimal,a pricetime int, and the current_user as arguments.
        The function then uploads the data to Rate table in database).

    :param ratename: str: Tariff name
    :param price: Decimal: Payment amount for the tiffin plan
    :param pricetime: int: The time for which the tariff payment amount is calculated
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A RateResponse object
    """ 
    if current_user.user_type_id not in (2, 3):
            raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    rate = await repository_admin.create_rate(rate_name, price, pricetime, current_user, db)
    return rate

@router.put("/update_rate", response_model=RateResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=2))],
            status_code=status.HTTP_200_OK)
async def update_rate(
    rate_name: str,  
    time_for_price: int,
    price: Decimal | None = None,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    """
    The update_rate function updates a rate .
        Args:
            - ratename (str): The str object containing the new data for the rate.
            - price (Decimal): The Decimal object containing the new data for the tariff price.
            - pricetime (int): The int object containing the new data for the pricetime.
            - db (AsyncSession, optional): [description]. Defaults to Depends(get_db).
            - current_user (User, optional): [description]. Defaults to Depends(auth_service.get_current_user).

    :param ratename: str: Tariff name
    :param price: Decimal: Payment amount for the tiffin plan
    :param pricetime: int: The time for which the tariff payment amount is calculated
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A RateResponse object
    """
    if current_user.user_type_id not in (2, 3):
            raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    rate = await repository_admin.update_rate(rate_name, price, time_for_price, db, current_user )
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATE_NOT_FOUND)
    return rate

@router.delete("/remove_rate",  status_code=status.HTTP_200_OK)
async def remove_rate(
    rate_name: str,\
    db: AsyncSession = Depends(get_db),\
    current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_rate function removes a rate from the database.

    :param ratename: str: Specify the rate name.
    :param current_user: User: Get the user who is currently logged in.
    :param db: AsyncSession: Pass the database session to the repository layer.
    :return: A Rate object
    """
    rate = await repository_admin.remove_rate(rate_name, db, current_user)
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATE_NOT_FOUND)
    return { "detail": "Rate deleted successfully"}

@router.post("/add_tariff_time", response_model=RateTimeResponse)
async def add_tariff_time(
        rate: str,
        monday: bool ,
        tuesday: bool,
        wednesday: bool,
        thursday: bool,
        friday: bool,
        saturday: bool,
        sunday: bool,
        starttime: time,
        stoptime: time,
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)):  
    """
    Function add_tariff_time for creating the validity period of a tariff plan.
       Input data: name of the tariff plan, days of the week and duration of the tariff plan.
   
    :param rate: str: Rate name
    :param monday: bool: Day of the week
    :param tuesday: bool: Day of the week
    :param wednesday: bool: Day of the week
    :param thursday: bool: Day of the week
    :param friday: bool: Day of the week
    :param saturday: bool: Day of the week
    :param sunday: bool: Day of the week
    :param starttime: time: Start of tariff plan  HH:MM:SS
    :param stoptime: time: Stщз of tariff plan   HH:MM:SS
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A RateTimeResponse object
    """
    if current_user.user_type_id not in (2, 3):
            raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    tariff_time = await repository_admin.add_tariff_time(rate, monday, tuesday, wednesday, thursday, friday, saturday, sunday,
        starttime,
        stoptime,
        current_user,
        db
        )
    return tariff_time

@router.put("/update_tariff_time", response_model=RateTimeResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=2))],
            status_code=status.HTTP_200_OK)
async def update_tariff_time(
    id_tariff_time: int,
    monday: bool,
    tuesday: bool,
    wednesday: bool,
    thursday: bool,
    friday: bool,
    saturday: bool,
    sunday: bool,
    starttime: time,
    stoptime: time,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
      ):
    """
    Function update_tariff_time for update the validity period of a tariff plan.
       Input data: name of the tariff plan, days of the week and duration of the tariff plan.
   
    :param rate: str: Rate name
    :param monday: bool: Day of the week
    :param tuesday: bool: Day of the week
    :param wednesday: bool: Day of the week
    :param thursday: bool: Day of the week
    :param friday: bool: Day of the week
    :param saturday: bool: Day of the week
    :param sunday: bool: Day of the week
    :param starttime: time: Start of tariff plan
    :param stoptime: time: Stщз of tariff plan
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A RateTimeResponse object
    """
    if current_user.user_type_id not in (2, 3):
            raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    tariff_time = await repository_admin.update_tariff_time(id_tariff_time, monday, tuesday, wednesday, thursday, friday, saturday, sunday,
        starttime,
        stoptime,
        current_user,
        db
          )
    if tariff_time is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.TARIF_TIME_NOT_FOUND)
    return tariff_time

@router.delete("/remove_tariff_time",  status_code=status.HTTP_200_OK)
async def remove_tariff_time(
    id_tariff_time: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    """
    Function remove_tariff_time for delete the validity period of a tariff plan.
       Input data: id tariff time ,

    :param id_tariff_time: int: Specify the post id
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: A Rate Time object
    """
    if current_user.user_type_id not in (2, 3):
            raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    tariff_time = await repository_admin.remove_tariff_time(id_tariff_time, db, current_user)
    if tariff_time is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.TARIF_TIME_NOT_FOUND)
    return { "detail": " deleted successfully"}

@router.get(
    "/rates_info",
    response_model=list[RateResponse],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
     )
async def rates_info(
    all_rates : bool,
    rate_name : str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    rates_info = await get_rates_info(all_rates, rate_name, db)
    """
    Function for displaying information about tariff plans. 
       Takes as input a logical value and the name of the tariff.
       If the logical expression is true, information about all tariffs is displayed;
       if not, information about the tariff by name is displayed.

    :param all_rates: int: Specify the post id
    :param db: AsyncSession: Get the database session
    :return: A Rate Time object
    """
    if rates_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATE_NOT_FOUND)
    return rates_info


