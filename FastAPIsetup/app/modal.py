from sqlalchemy import Column, Integer, String

try:
    from .database import Base
except ImportError:  # pragma: no cover - allows direct script execution
    from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    auth_version = Column(Integer, nullable=False, default=0)


class Config:
    orm_mode = True
