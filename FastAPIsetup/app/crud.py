import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

try:
    from .database import get_db
    from .modal import User
    from .schems import create_user as CreateUserSchema, get_users
except ImportError:  # pragma: no cover - allows running via main.py directly
    from database import get_db
    from modal import User
    from schems import create_user as CreateUserSchema, get_users

router = APIRouter(prefix="/main", tags=["Users"])
logger = logging.getLogger(__name__)


@router.get("/users", response_model=list[get_users])
def get_allusers(db: Session = Depends(get_db)):
    """Return all users from the database."""
    logger.info("Fetching all users")
    return db.query(User).all()


@router.post("/create_user", response_model=get_users)
def create_user_record(user: CreateUserSchema, db: Session = Depends(get_db)):
    """Create a new user in the database."""
    logger.info("Creating a new user")
    new_user = User(name=user.name, password=user.password, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user