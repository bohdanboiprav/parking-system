import redis
from fastapi import Depends, HTTPException, UploadFile, File
from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.entity.models import User ,Avto
from src.schemas.user import UserSchema , AvtoResponse
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

async def add_avto(body: AvtoResponse, current_user: User, db: AsyncSession) :
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
    avto = select(Avto).filter_by(user=current_user).filter(Avto.number == body.number)
    avto = await db.execute(avto)
    avto = avto.scalars().first()
    if avto:
        raise HTTPException(status_code=400, detail="Avto with this number already exists")
    avto = Avto(
        number=body.number,
        color=body.color,
        model=body.model,
        user=current_user)
    db.add(avto)
    await db.commit()
    await db.refresh(avto)
    return avto

async def update_avto(
    db: AsyncSession,
    user: User,
    number: str  ,
    new_number: str  ,
    color: str | None = None ,
    model: str | None = None , 
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
    avto =  select(Avto).filter_by(number=number)
    avto = await db.execute(avto)
    avto = avto.scalars().first()
    if not avto:
        raise HTTPException(status_code=404, detail=messages.AVTO_NOT_FOUND)
    if avto.user_id != user.id:
        raise HTTPException(status_code=403, detail=messages.AVTO_NOT_PERMISSION)
    avto.number = new_number
    avto.color = color
    avto.model = model
    await db.commit()
    await db.refresh(avto)

    return avto

async def ban_user(username: str, db: AsyncSession):
    """
    The ban_user function takes a username and an asyncpg database connection as arguments.
    It then queries the database for the user with that username, and if it finds one, sets their is_banned flag to True.
    The function also deletes any refresh tokens associated with that user from Redis.

    :param username: str: Specify the username of the user to be banned
    :param db: AsyncSession: Pass in the database session
    :return: The user object
    """
    user = await get_user_by_username(username, db)
    if user:
        cache = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            password=settings.REDIS_PASSWORD,
        )
        user.is_banned = True
        user.refresh_token = None
        cache.delete(str(user.email))
        await db.commit()
        await db.refresh(user)
        return user