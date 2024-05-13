import uuid
from datetime import datetime , date ,time
from pydantic import BaseModel, EmailStr, ConfigDict, Field 
from decimal import Decimal
from typing import List, Optional ,Dict

class AvtoResponse(BaseModel):
    number: str | None 
    color: str | None 
    model: str | None 

class AdminUserResponse(BaseModel):
    firstname: str | None 
    lastname: str | None 
    email: EmailStr
    mobilenamber: str | None
    databirthday: date | None
    balance: Decimal | None
    notification: bool 
    avatar: str
    all_avto: List[AvtoResponse] | None
    model_config = ConfigDict(from_attributes=True)