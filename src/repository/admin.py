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

async def get_admin_users_info(limit, offset, user: User, db: AsyncSession = Depends(get_db)):
    
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
    If no such user exists, it returns None.

    :param email: str: Pass the email of the user to be retrieved
    :param db: AsyncSession: Pass in the database session
    :return: A user object or none
    """
    if user.user_type_id not in (2, 3):
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    stmt = select(User).offset(offset).limit(limit)
    stmp = await db.execute(stmt)
    info = stmp.scalars().unique().all()
    return info

async def get_user_info(user: User, db: AsyncSession = Depends(get_db)):
    
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
    If no such user exists, it returns None.

    :param email: str: Pass the email of the user to be retrieved
    :param db: AsyncSession: Pass in the database session
    :return: A user object or none
    """

    stmt = select(User).filter_by(email=user.email)
    stmp = await db.execute(stmt)
    info = stmp.scalars().unique().all()
    return info
    
async def get_number_avto(number, email: str, db: AsyncSession = Depends(get_db)):
    
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
    If no such user exists, it returns None.

    :param email: str: Pass the email of the user to be retrieved
    :param db: AsyncSession: Pass in the database session
    :return: A user object or none
    """
    
    stmt = select(User).join(Avto).filter_by(number = number)
    user = await db.execute(stmt)
    user = user.scalars().unique().all()
    return user


async def get_log_info(all_info ,number_avto, limit: int, offset: int, user: User, db: AsyncSession ):
    
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
    If no such user exists, it returns None.

    :param email: str: Pass the email of the user to be retrieved
    :param db: AsyncSession: Pass in the database session
    :return: A user object or none
    """

    stmt = select(User).filter_by(email=user.email)
    user = await db.execute(stmt)
    user = user.scalars().first()
    if not user:
            raise HTTPException(status_code=404, detail=messages.AVTO_NOT_FOUND) 
    else:
        if all_info == True:
            c = len(user.all_avto) - 1
            for number in c :
                user.all_avto[number].number
        else:
            for num in range(len(user.all_avto)) :
                if user.all_avto[num].number == number_avto :
                    stmt = select(Log).filter(Log.number == number_avto).offset(offset).limit(limit)
                    info = await db.execute(stmt)
                    info = info.scalars().unique().all()
                    return info 
