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



async def get_user_by_email(email, user: str, db: AsyncSession = Depends(get_db)):
    
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

async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):

    """
    The get_user_by_username function takes a username and returns the user object associated with that username.
    If no such user exists, it returns None.

    :param username: str: Specify the username of the user we want to retrieve
    :param db: AsyncSession: Pass the database session into the function
    :return: A user object or none
    """

    stmt = select(User).filter_by(username=username)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


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
    The add_tag_to_post function adds a tag to the post.
        Args:
            - body (TagUpdate): The TagUpdate object containing the name of the post and tags to add.
            - current_user (User): The User object representing who is making this request.
            - db (AsyncSession): A database session for interacting with Postgresql via SQLAlchemy Core.

    :param body: TagUpdate: Get the name of the post and tags to add
    :param current_user: User: Check if the user is authorized to add tags to a post
    :param db: AsyncSession: Pass the database session to the function
    :return: A post with a new tag
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
    new_number: str,
    db: AsyncSession,
    user: User,
    color: str | None = None,
    model: str | None = None, 
    ):

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

    avto = select(Avto).filter_by(user=user).filter(Avto.number == number)
    avto = await db.execute(avto)
    avto = avto.scalars().first()
    if avto is None:
        raise HTTPException(status_code=404, detail=messages.AVTO_NOT_FOUND)
    if avto.user_id != user.id:
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    avto_new = select(Avto).filter_by(user=user).filter(Avto.number == new_number)
    avto_new = await db.execute(avto_new)
    avto_new = avto_new.scalars().first()
    if avto_new :
        raise HTTPException(status_code=404, detail=messages.AVTO_IS_EXISTS)
    avto.number = new_number
    avto.color = color
    avto.model = model
    db.add(avto)
    await db.commit()
    await db.refresh(avto)
    return avto

async def remove_avto(number: str, db: AsyncSession, current_user: User,):
    """
    The remove_post function removes a post from the database.
        Args:
            - post_id (int): The id of the post to be removed.
            - current_user (User): The user who is making this request. This is used to ensure that only the owner of a
            - particular post can remove it, and not other users.


    :param post_id: int: Get the post from the database
    :param current_user: User: Ensure that the user is logged in
    :param db: AsyncSession: Connect to the database
    :return: The post that was removed
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

async def get_rates_info(db: AsyncSession = Depends(get_db)):
    
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
    If no such user exists, it returns None.

    :param email: str: Pass the email of the user to be retrieved
    :param db: AsyncSession: Pass in the database session
    :return: A user object or none
    """

    stmt = select(Rate)
    contacts =  await db.execute(stmt)
    return contacts.scalars().unique().all()
    
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
