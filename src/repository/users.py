import redis
from fastapi import Depends, HTTPException, UploadFile, File
from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.entity.models import User, Avto, Rate ,Log
from src.schemas.user import UserSchema, AvtoResponse, RateResponse, RateTimeResponse
from typing import List
from src.conf import messages

async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
    If no such user exists, it returns None.

    :param email: str: Pass the email of the user to be retrieved
    :param db: AsyncSession: Pass in the database session
    :return: A user object or none
    """
 
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalars().first()
    return user

async def get_user_info(user: User, db: AsyncSession = Depends(get_db)):
    
    """
    The get_user_info function takes an email address and returns the user associated with that email.
    If no such user exists, it returns None.

    :param email: str: Pass the email of the user to be retrieved
    :param db: AsyncSession: Pass in the database session
    :return: A user object or none
    """

    stmt = select(User).filter_by(email=user.email)
    stmp = await db.execute(stmt)
    info = stmp.scalars().unique().all()
    return info

async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):

    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the data that is passed into the function
    :param db: AsyncSession: Get the database session
    :return: The newly created user object
    """

    avatar = 'https://asset.cloudinary.com/dkprmxdfc/cbcb3e506c226483c2be7155f6e3ff7c'
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar, user_type_id=1)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user in the database
    :param token: str | None: Specify the type of the token parameter
    :param db: AsyncSession: Commit the changes to the database
    :return: The user object
    """

    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:

    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.

    :param email: str: Get the email of the user that is being confirmed
    :param db: AsyncSession: Pass in the database session
    :return: None
    """

    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:

    """
    The update_avatar_url function updates the avatar url of a user.

    :param email: str: Specify the email of the user to update
    :param url: str | None: Specify that the url parameter can be a string or none
    :param db: AsyncSession: Pass in the database session
    :return: The updated user
    """

    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user

async def add_avto(number, color, model, current_user: User, db: AsyncSession) :
    """
    The function of adding car data to the database. Accepts the number, color and size of the car.

    :param number: str or None: Car`s number
    :param colour: str or None: Car`s colour
    :param model: str or None: Car`s model
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: The created avto with the new id
    """
    avto = select(Avto).filter_by(user=current_user).filter(Avto.number == number)
    avto = await db.execute(avto)
    avto = avto.scalars().first()
    if avto:
        raise HTTPException(status_code=400, detail=messages.AVTO_IS_EXISTS)
    avto = Avto(
        number=number,
        color=color,
        model=model,
        user=current_user)
    db.add(avto)
    await db.commit()
    await db.refresh(avto)
    return avto

async def update_avto(
    number: str,
    db: AsyncSession,
    user: User,
    color: str | None = None,
    model: str | None = None, 
    ):
    """
    The update_avto function updates a Avto's data.
        Args:

    :param number: str or None: Car`s number
    :param colour: str or None: Car`s colour
    :param model: str or None: Car`s model
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A avto object
    """
    avto = select(Avto).filter_by(user=user).filter(Avto.number == number)
    avto = await db.execute(avto)
    avto = avto.scalars().first()
    if avto is None:
        raise HTTPException(status_code=404, detail=messages.AVTO_NOT_FOUND)
    if avto.user_id != user.id:
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    avto.color = color
    avto.model = model
    db.add(avto)
    await db.commit()
    await db.refresh(avto)
    return avto

async def remove_avto(number: str, db: AsyncSession, current_user: User,):
    """
    The remove_avto function removes a avto from the database.

    :param number: str: Specify the avto number
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: The removed avto
    """
    avto = select(Avto).filter_by(user=current_user).filter(Avto.number == number)
    avto = await db.execute(avto)
    avto = avto.scalars().first()
    if not avto:
        raise HTTPException(status_code=404, detail=messages.AVTO_NOT_FOUND)
    if avto.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    await db.commit()
    await db.delete(avto)
    await db.commit()
    return avto

async def get_rates_info(all_rates, rate_name, db: AsyncSession = Depends(get_db)):
    """
    Function for displaying information about tariffs in the park.

    :param all_rates: Bool: A logical evolution if it is true to search for all tariffs.
    :param rate_name: str | None = None: Rate name info
    :return: A rates object
    """
    if all_rates == True:
        rates = select(Rate)
        rates =  await db.execute(rates)
        rates =  rates.scalars().unique().all()
        if not rates:
            raise HTTPException(status_code=404, detail=messages.RATE_NOT_FOUND)
        return rates
    else:
        rate = select(Rate).filter_by(ratename = rate_name)
        rate =  await db.execute(rate)
        rate =  rate.scalars().unique().all()
        if not rate:
            raise HTTPException(status_code=404, detail=messages.RATE_NOT_FOUND)
        return rate
  
async def get_log_info(number_avto, limit: int, offset: int, user: User, db: AsyncSession ):
    """
    Function for searching user parking visit data in the database.

    :param all_info: bool: A logical evolution if it is true to search for all tariffs.
    :param number: str: Specify the type of object that is returned by the auth_service
    :param limit (int): The maximum number of users in the function response.
    :param offset(int): The minimum number of users in the function response.
    :param user: User: Specify the type of object that is returned by the auth_service
    :return: Log list
    """
    stmt = select(User).filter_by(email=user.email)
    user = await db.execute(stmt)
    user = user.scalars().first()
    if not user:
            raise HTTPException(status_code=404, detail=messages.AVTO_NOT_FOUND)
    res = [num.number for num in user.all_avto]

    print(res)
    if number_avto not in [num.number for num in user.all_avto]:
        raise HTTPException(status_code=404, detail=messages.AVTO_NOT_FOUND)
    stmt = select(Log).filter(Log.number == number_avto).offset(offset).limit(limit)
    info = await db.execute(stmt)
    info = info.scalars().unique().all()
    return info 

