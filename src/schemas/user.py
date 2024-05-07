import uuid
from datetime import datetime 
from pydantic import BaseModel, EmailStr, ConfigDict, Field 
from decimal import Decimal
from typing import List, Optional ,Dict

class UserSchema(BaseModel):
    #username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)

class AvtoResponse(BaseModel):
    number: str | None 
    color: str | None 
    model: str | None 

class UserResponse(BaseModel):
    firstname: str | None 
    lastname: str | None 
    email: EmailStr
    mobilenamber: str | None
    databirthday: datetime | None
    balance: Decimal | None
    notification: bool 
    avatar: str
    all_avto: List[AvtoResponse] | None
    model_config = ConfigDict(from_attributes=True)
    



class UserProfileResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    avatar: str
    created_at: str
    updated_at: str
    model_config = ConfigDict(from_attributes=True)


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class UpdateProfile(BaseModel):
    username: str | None = Field()