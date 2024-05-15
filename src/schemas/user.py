import uuid
from datetime import datetime , date ,time
from pydantic import BaseModel, EmailStr, ConfigDict, Field 
from decimal import Decimal
from typing import List, Optional ,Dict

class UserSchema(BaseModel):
    #username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)

class UserUpdateSchema(BaseModel):
    firstname: str | None 
    lastname: str | None 
    mobilenamber: str | None
    databirthday: datetime | None
    notification: bool 

  

class AvtoResponse(BaseModel):
    number: str | None 
    color: str | None 
    model: str | None 

class UserResponse(BaseModel):
    firstname: str | None 
    lastname: str | None 
    email: EmailStr
    mobilenamber: str | None
    databirthday: date | None
    balance: Decimal | None
    notification: bool | None
    avatar: str
    all_avto: List[AvtoResponse] | None
    model_config = ConfigDict(from_attributes=True)

class RateTimeResponse(BaseModel):
    id : int | None
    monday: bool | None
    tuesday: bool | None
    wednesday: bool | None
    thursday: bool | None
    friday: bool | None
    saturday: bool | None
    sunday: bool | None
    starttime: time | None
    stoptime: time  | None

    
class RateResponse(BaseModel):
    ratename: str | None
    price: Decimal | None
    pricetime: int | None
    ratestime: List[RateTimeResponse] | None
    model_config = ConfigDict(from_attributes=True)

class LogResponse(BaseModel):
    number: str | None
    start: datetime | None
    stop: datetime | None
    total: Decimal | None
    discount: Decimal | None  
    in_parking : bool | None 
   


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