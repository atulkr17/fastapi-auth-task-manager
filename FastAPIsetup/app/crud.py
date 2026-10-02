import logging

from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.orm import Session

try:
    from .database import get_db
    from .modal import User
    from .schems import create_user, get_users, update_user
except ImportError:  # pragma: no cover - allows running via main.py directly
    from database import get_db
    from modal import User
    from schems import create_user, get_users, update_user

router = APIRouter(prefix="/main", tags=["Users"])
logger = logging.getLogger(__name__)


@router.get("/users", response_model=list[get_users])
def get_allusers(db: Session = Depends(get_db)):
    """Return all users from the database."""
    logger.info("Fetching all users")
    return db.query(User).all()


@router.post("/create_user", response_model=get_users)
def create_user_record(user:  create_user, db: Session = Depends(get_db)):
    """Create a new user in the database."""
    logger.info("Creating a new user")
    new_user = User(name=user.name, password=user.password, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users/{user_id}", response_model=get_users)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Return a user by ID from the database."""
    logger.info("Fetching user with ID: %s", user_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning("User with ID %s not found", user_id)
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/users/{user_id}", response_model=get_users)
def delete_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Delete a user by ID from the database."""
    logger.info("Deleting user with ID: %s", user_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning("User with ID %s not found for deletion", user_id)
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user

@router.put("/users/{user_id}", response_model=get_users)
def update_user_by_id(user_id: int, user_update: update_user, db: Session = Depends(get_db)):
    """Update a user by ID in the database."""
    logger.info("Updating user with ID: %s", user_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning("User with ID %s not found for update", user_id)
        raise HTTPException(status_code=404, detail="User not found")
    
    user.name = user_update.name
    user.password = user_update.password
    user.email = user_update.email
    db.commit()
    db.refresh(user)
    return user   