from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
    Response, Query,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from fastapi.responses import FileResponse
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import users as repository_users
from src.repository.log import enter_log, exit_log
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email_ import send_email
from src.conf import messages
from src.services.get_photo import capture_and_save_image
from src.services.plates import plates_recognition, model

router = APIRouter(prefix="/plates", tags=["plates"])
get_refresh_token = HTTPBearer()
get_access_token = HTTPBearer()


@router.get("/parking_enter", dependencies=[Depends(RateLimiter(times=2, seconds=5))], )
async def parking_enter(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)):
    if user.user_type_id != 3:
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    # image_path = await capture_and_save_image()
    plates_number = await plates_recognition('src/routes/1.jpeg', model)
    plates_number = plates_number.strip().replace('\n', "")

    print(plates_number)
    if plates_number is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PLATES_NOT_RECOGNIZED)
    log = await enter_log(plates_number, user, db)
    return log


@router.get("/parking_exit", dependencies=[Depends(RateLimiter(times=2, seconds=5))], )
async def parking_exit(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)):
    if user.user_type_id != 3:
        raise HTTPException(status_code=403, detail=messages.USER_NOT_PERMISSION)
    # image_path = await capture_and_save_image()
    plates_number = await plates_recognition('src/routes/1.jpeg', model)
    plates_number = plates_number.strip().replace('\n', "")
    print(plates_number)
    if plates_number is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PLATES_NOT_RECOGNIZED)
    log = await exit_log(plates_number, user, db, discount=0)
    return log
