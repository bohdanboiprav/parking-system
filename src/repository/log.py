from datetime import datetime, timezone
from decimal import Decimal

import redis
from fastapi import Depends, HTTPException, UploadFile, File
from libgravatar import Gravatar
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.entity.models import User, Avto, Rate, Log, RateTime
from src.schemas.user import UserSchema, AvtoResponse, RateResponse, RateTimeResponse
from typing import List
from src.conf import messages


async def enter_log(number, current_user: User, db: AsyncSession):
    if current_user.user_type_id != 3:
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    log = Log(
        number=number,
        in_parking=True)
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def exit_log(number, current_user: User, db: AsyncSession, discount=0):
    if current_user.user_type_id != 3:
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    existing_log = await db.execute(select(Log).where(Log.number == number and Log.in_parking is True))
    log = existing_log.scalars().first()
    print(log)
    if log is None:
        raise HTTPException(status_code=404, detail=messages.LOG_NOT_FOUND)
    entered_day = log.start.strftime("%A").lower()
    rate = await db.execute(select(Rate).join(Rate.ratestime).filter(getattr(RateTime, entered_day) == True))
    rate = rate.scalars().first()
    entered_time = log.start
    print(entered_time)
    print('-' * 100)
    time_difference = datetime.now(timezone.utc) - entered_time
    print(time_difference)
    time_difference_minutes = time_difference.total_seconds() / 60
    total_value = rate.price * Decimal(time_difference_minutes) / rate.pricetime
    log.in_parking = False
    log.stop = func.now()
    log.total = Decimal(total_value)
    log.discount = discount
    user = await db.execute(select(User).join(Avto).where(Avto.user_id == User.id).where(Avto.number == number))
    user = user.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail=messages.USER_NOT_FOUND)
    user.balance -= Decimal(log.total) - Decimal(log.discount)
    await db.commit()
    await db.refresh(log)
    await db.refresh(user)
    return log
