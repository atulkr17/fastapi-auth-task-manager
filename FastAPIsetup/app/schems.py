from pydantic import BaseModel, ConfigDict


class get_users(BaseModel):
    id: int
    name: str
    email: str | None = None
    auth_version: int = 0

    model_config = ConfigDict(from_attributes=True)

class create_user(BaseModel):
    name: str
    password: str
    email: str | None = None

    model_config = ConfigDict(from_attributes=True)