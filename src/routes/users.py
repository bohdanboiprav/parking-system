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
from src.repository.users import get_log_info, get_rates_info, get_user_info
from src.schemas.user import LogResponse,RateResponse, AvtoResponse, UserResponse
from src.services.auth import auth_service
from src.repository import users as repository_users
from src.repository import profile as repository_profile

router = APIRouter(prefix="/users", tags=["users"])
configure_cloudinary()


@router.get(
    "/me",
    response_model=list[UserResponse],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_current_user(db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param user: User: Specify the type of object that is returned by the auth_service
    :return: The current user, which is stored in the database
    """
    aboutme = await get_user_info(user, db)
    if aboutme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
    return aboutme

@router.put("/profile/update", response_model=UserResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=2))],
            status_code=status.HTTP_200_OK)
async def update_user_profile(
    notification: bool ,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
    firstname: str | None = None ,
    lastname: str | None = None ,
    mobilenamber: str | None = None,
    databirthday: date | None = None,
     ):
    """
    The update_user_profile function updates a user's profile.
        Args:
            - db (AsyncSession, optional): [description]. Defaults to Depends(get_db).
            - current_user (User, optional): [description]. Defaults to Depends(auth_service.get_current_user).
            - firstname: Users firstname
            - lastname: Users lastname
            - mobilenamber: Users mobilenamber
            - databirthday: Users databirthday  YYYY-MM-DD

    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :param firstname: str or None: Users firstname
    :param lastname: str or None: Users lastname
    :param mobilenamber: str or None: Users mobilenamber
    :param databirthday: date or None: Users databirthday
    :return: A user object
    """
    user = await repository_profile.update_user_profile(
        notification,
        db,
        current_user,
        firstname ,
        lastname ,
        mobilenamber,
        databirthday,
          )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
    return user



@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_current_user(
        file: UploadFile = File(),
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It takes in an UploadFile object, which is a file
        uploaded by the user, and uses it to update their avatar URL on Cloudinary.

    :param file: UploadFile: Get the file from the request
    :param user: User: Get the current user
    :param db: AsyncSession: Get the database connection
    :return: The current user
    """
    public_id = f"Photoshare_app/Avatars/{user.id}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(res["public_id"]).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repository_users.update_avatar_url(user.email, res_url, db)
    return user

@router.post("/add_avto", response_model=AvtoResponse)
async def create_post(
        number: str,
        colour: str | None = None,
        model: str | None = None,
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)):
    
    """
    The function of adding car data to the database. Accepts the number, color and size of the car.

    :param number: str or None: Cars number
    :param colour: str or None: Cars colour
    :param model: str or None: Cars model
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: The created avto with the new id
    """

    avto = await repository_users.add_avto(number, colour, model, user, db)
    return avto

@router.put("/update_avto", response_model=AvtoResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=2))],
            status_code=status.HTTP_200_OK)
async def update_avto(
    number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
    color: str | None = None,
    model: str | None = None,
     ):
    """
    The update_avto function updates a Avto's data.
        Args:

    :param number: str or None: Cars number
    :param colour: str or None: Cars colour
    :param model: str or None: Cars model
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A avto object
    """
    avto = await repository_users.update_avto(
        number,
        db,
        current_user,
        color,
        model ,
          )

    if avto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.AVTO_NOT_FOUND)
    return avto

@router.delete("/remove_avto",  status_code=status.HTTP_200_OK)
async def remove_avto(number: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)):
    """
    The remove_avto function removes a avto from the database.

    :param number: str: Specify the avto number
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: The removed avto
    """
    avto = await repository_users.remove_avto(number, db, user)
    if avto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.AVTO_NOT_FOUND)
    return { "detail": "Avto deleted successfully"}

@router.get(
    "/rates_info",
    response_model=list[RateResponse],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def rates_info(
    all_rates : bool,
    rate_name : str | None = None,
    db: AsyncSession = Depends(get_db)):
    """
    Function for displaying information about tariffs in the park.

    :param all_rates: Bool: A logical evolution if it is true to search for all tariffs.
    :param rate_name: str | None = None: Rate name info
    :return: A rates object
    """
    rates_info = await get_rates_info(all_rates,rate_name, db)
    if rates_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATE_NOT_FOUND)
    return rates_info

@router.get(
    "/statistics",
    #response_model=list[LogResponse],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_statistics(
        number: str | None = None,
        limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user),       
        ):
    """
    Function for searching user parking visit data in the database.

    :param all_info: bool: A logical evolution if it is true to search for all tariffs.
    :param number: str: Specify the type of object that is returned by the auth_service
    :param limit (int): The maximum number of users in the function response.
    :param offset(int): The minimum number of users in the function response.
    :param user: User: Specify the type of object that is returned by the auth_service
    :return: Log list
    """
    log = await get_log_info(number, limit, offset,user, db)
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.LOG_NOT_FOUND)
    return log

