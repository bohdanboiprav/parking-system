from datetime import datetime, date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User
from src.schemas.user import UserSchema,UserUpdateSchema
from fastapi import Depends, HTTPException, UploadFile, File
from src.conf import messages

async def update_user_profile(
    notification: bool ,
    db: AsyncSession,
    user: User,
    firstname: str ,
    lastname: str | None = None ,
    mobilenamber: str | None = None ,
    databirthday: date | None = None ,   
    ) :

    """
    The update_user_profile function updates a user's profile information.
        Args:
            - body (UserSchema): The UserSchema object containing the new user data.
            - user (User): The User object to be updated.

    :param body: UserSchema: Get the data from the request body
    :param user: User: Get the user object from the database
    :param db: AsyncSession: Pass in the database session
    :return: The updated user object
    """
    stmt = select(User).filter_by(email=user.email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user:
        user.firstname = firstname
        user.lastname = lastname
        user.mobilenamber = mobilenamber
        user.databirthday = databirthday
        user.notification = notification
        user.updated_at = datetime.now()

        await db.commit()
        await db.refresh(user)
    return user

async def update_admin_user_profile(
    email: str,
  #  notification,
    db: AsyncSession,
    user: User,
    firstname: str ,
    lastname: str | None = None ,
    mobilenamber: str | None = None ,
    databirthday: date | None = None ,   
    ) -> User | None:
    """
    The update_user_profile function updates a user's profile information.
        Args:
            - body (UserSchema): The UserSchema object containing the new user data.
            - user (User): The User object to be updated.

    :param body: UserSchema: Get the data from the request body
    :param user: User: Get the user object from the database
    :param db: AsyncSession: Pass in the database session
    :return: The updated user object
    """
    if user.user_type_id not in (2, 3):
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    stmt = select(User).filter_by(email=email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user:
        user.firstname = firstname
        user.lastname = lastname
        user.mobilenamber = mobilenamber
        user.databirthday = databirthday
       # user.notification = notification,
        user.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(user)
    return user
