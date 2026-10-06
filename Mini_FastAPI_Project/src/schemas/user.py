from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    medialname: str | None = None
    

class UserSignup(UserCreate):
    pass

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    medialname: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    medialname: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserSignin(BaseModel):

    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


