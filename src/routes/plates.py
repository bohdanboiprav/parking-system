from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
    Response,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import users as repository_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email
from src.conf import messages

router = APIRouter(prefix="/plates", tags=["plates"])
get_refresh_token = HTTPBearer()
get_access_token = HTTPBearer()


async def get_current_user(db: AsyncSession = Depends(get_db),
                           credentials: HTTPAuthorizationCredentials = Security(get_access_token)) -> User:
    return await auth_service.get_current_user(db, credentials)
