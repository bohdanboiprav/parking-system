import redis
from fastapi import Depends, HTTPException, UploadFile, File
from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.entity.models import User, Avto, Rate , Log, RateTime
from src.schemas.user import UserSchema, AvtoResponse, RateResponse, RateTimeResponse
from typing import List
from src.conf import messages
from sqlalchemy import Boolean

async def update_balans(
    email,
    replenishment,
    db: AsyncSession,
    user: User, 
    ) :
    """
   The replenishment_of_balags function updates a user's balance.
        Args:
            - email(str): str object containing the user's email
            - replenishment (Decimal): User's account top-up amount
            - db (AsyncSession, optional): [description]. Defaults to Depends(get_db).
            - current_user (User, option.

    :param email: str: User`s email
    :param replenishment: Decimal: Get the connection to the database
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A user object
    """
    carer = select(User).filter_by(email=email)
    carent_user = await db.execute(carer)
    carent_user = carent_user.scalars().first()
    if not carent_user:
        raise HTTPException(status_code=404, detail=messages.USER_NOT_FOUND)
    if replenishment == None:
        raise HTTPException(status_code=400, detail=messages.NO_DATA)
    if carent_user.balance == None:
        carent_user.balance = 0 
    print(replenishment)
    carent_user.balance = replenishment + carent_user.balance
    db.add(carent_user)
    await db.commit()
    await db.refresh(carent_user)
    return {"balance replenished by sum": replenishment,"total balance": carent_user.balance}

async def get_admin_users_info(email, limit, offset, user: User, db: AsyncSession = Depends(get_db)): 
    """
    The function get_admin_users_info receives the input mail or None if the input is None,
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
    if email == None :
        stmt = select(User).offset(offset).limit(limit)
        stmp = await db.execute(stmt)
        info = stmp.scalars().unique().all()
        return info
    else :
        stmt = select(User).filter_by(email=email).offset(offset).limit(limit)
        stmp = await db.execute(stmt)
        info = stmp.scalars().unique().all()
        return info        
   
async def get_number_avto(number, db: AsyncSession = Depends(get_db)):
    """
    The get_number_avto function for searching information about 
        a car by number. Receives the car number as input.
    
    :param number: str: User`s number avto
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A users object
    """
    stmt = select(User).join(Avto).filter_by(number = number)
    user = await db.execute(stmt)
    user = user.scalars().first()
    result = {
        "number": number,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "mobilenamber": user.mobilenamber,
        "databirthday": user.databirthday,
        "balance": user.balance,
        "notification": user.notification,
        "avatar": user.avatar,
        "created_at": user.created_at,
        "confirmed": user.confirmed,
        "is_banned": user.is_banned,
        "all_avno": user.all_avto,

        }
    return result

async def ban_avto(
    is_ban: bool,    
    number: str,
    db: AsyncSession,
    user: User,
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
    avto = select(Avto).filter_by(number=number)
    avto = await db.execute(avto)
    avto = avto.scalars().first()
    if avto is None:
        raise HTTPException(status_code=404, detail=messages.AVTO_NOT_FOUND)
    avto.is_banned = is_ban
    db.add(avto)
    await db.commit()
    await db.refresh(avto)
    return avto

async def remove_avto(number: str, db: AsyncSession, user: User,):
    """
    Function remove_avto for delete a car with the database.

    :param number: Number avto
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A user object
    """
    avto = select(Avto).filter_by(number=number)
    avto = await db.execute(avto)
    avto = avto.scalars().first()
    if not avto:
        raise HTTPException(status_code=404, detail=messages.AVTO_NOT_FOUND)
    await db.commit()
    await db.delete(avto)
    await db.commit()
    return avto

async def get_ban_avto(limit, offset, user: User, db: AsyncSession = Depends(get_db)):
    """   
    Search get_ban_avto function for blocked cars in the database.

    :param limit (int): The maximum number of users in the function response.
    :param offset(int): The minimum number of users in the function response.
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A avto object
    """
    stmt = select(Avto).filter_by(is_banned=True).offset(offset).limit(limit)
    stmp = await db.execute(stmt)
    info = stmp.scalars().unique().all()
    return info

async def create_rate(ratename, price, pricetime, user: User, db: AsyncSession) :
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
    rate = select(Rate).filter_by(ratename=ratename)
    rate = await db.execute(rate)
    rate = rate.scalars().first()
    if rate:
        raise HTTPException(status_code=400, detail=messages.RATE_IS_EXISTS)
    rate = Rate(ratename=ratename, price=price, pricetime=pricetime)
    db.add(rate)
    await db.commit()
    await db.refresh(rate)
    return rate

async def update_rate(
    ratename, 
    price ,
    pricetime, 
    db: AsyncSession,
    user: User
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
    rate = select(Rate).filter_by(ratename=ratename)
    rate = await db.execute(rate)
    rate = rate.scalars().first()
    if rate is None:
        raise HTTPException(status_code=404, detail=messages.RATE_NOT_FOUND)
    if price == None:
        raise HTTPException(status_code=404, detail=messages.NO_DATA)
    rate.ratename = ratename
    rate.price  = price 
    rate.pricetime = pricetime
    db.add(rate)
    await db.commit()
    await db.refresh(rate)
    return rate

async def remove_rate(ratename: str, db: AsyncSession, user: User,):
    """
    The remove_rate function removes a rate from the database.

    :param ratename: str: Specify the rate name.
    :param current_user: User: Get the user who is currently logged in.
    :param db: AsyncSession: Pass the database session to the repository layer.
    :return: A Rate object
    """
    rate = select(Rate).filter_by(ratename=ratename)
    rate = await db.execute(rate)
    rate = rate.scalars().first()
    if not rate:
        raise HTTPException(status_code=404, detail=messages.RATE_NOT_FOUND)
    await db.commit()
    await db.delete(rate)
    await db.commit()
    return rate

async def add_tariff_time(ratename, monday, tuesday, wednesday, thursday, friday, saturday, sunday,
        starttime,
        stoptime,
        user: User, db: AsyncSession) :
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
    :param starttime: time: Start of tariff plan
    :param stoptime: time: Stщз of tariff plan
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A RateTimeResponse object
    """
    rate = select(Rate).filter_by(ratename=ratename)
    rate = await db.execute(rate)
    rate = rate.scalars().first()
    if not rate:
        raise HTTPException(status_code=400, detail=messages.TARIF_TIME_NOT_FOUND)
    tariff_time = RateTime(
        monday = monday ,
        tuesday = tuesday,
        wednesday = wednesday,
        thursday = thursday,
        friday = friday,
        saturday = saturday,
        sunday = sunday,
        starttime = starttime,
        stoptime = stoptime,
        rate_id = rate.id
      )
    db.add(tariff_time)
    await db.commit()
    await db.refresh(tariff_time)
    return tariff_time

async def update_tariff_time(id_tariff_time, monday, tuesday, wednesday, thursday, friday, saturday, sunday,
    starttime,
    stoptime,
    user: User,
    db: AsyncSession,
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
    tariff_time = select(RateTime).filter_by(id=id_tariff_time)
    tariff_time = await db.execute(tariff_time)
    tariff_time = tariff_time.scalars().first()
    if tariff_time is None:
        raise HTTPException(status_code=404, detail=messages.TARIF_TIME_NOT_FOUND)
    tariff_time.monday = monday
    tariff_time.tuesday = tuesday
    tariff_time.wednesday = wednesday 
    tariff_time.thursday = thursday
    tariff_time.friday = friday
    tariff_time.saturday = saturday
    tariff_time.sunday = sunday
    tariff_time.starttime = starttime
    tariff_time.stoptime = stoptime
    db.add(tariff_time)
    await db.commit()
    await db.refresh(tariff_time)
    return tariff_time

async def remove_tariff_time(id_tariff_time: str, db: AsyncSession, user: User,):
    """
    Function remove_tariff_time for delete the validity period of a tariff plan.
       Input data: id tariff time ,

    :param id_tariff_time: int: Specify the post id
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: A Rate Time object
    """
    tariff_time = select(RateTime).filter_by(id=id_tariff_time)
    tariff_time = await db.execute(tariff_time)
    tariff_time = tariff_time.scalars().first()
    if tariff_time is None:
        raise HTTPException(status_code=404, detail=messages.TARIF_TIME_NOT_FOUND)
    await db.commit()
    await db.delete(tariff_time)
    await db.commit()
    return tariff_time


