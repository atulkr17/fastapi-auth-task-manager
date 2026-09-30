from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: str = "pending"


class TaskUpdate(BaseModel):
    title: str
    description: str | None
    status: str


class TaskPartialUpdate(BaseModel):
    title: str = Field(default=None)
    description: str | None = None
    status: str = Field(default=None)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"