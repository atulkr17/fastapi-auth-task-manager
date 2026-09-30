import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a user account after checking that its email is available."""
    logger.info("User registration started")
    email = str(user.email).lower()
    logger.debug("Checking whether the registration email is already in use")
    try:
        existing_user = db.query(models.User).filter(models.User.email == email).first()
    except Exception as error:
        logger.error("Registration lookup failed (%s)", type(error).__name__)
        raise
    if existing_user:
        logger.warning("Registration rejected because the email is already registered")
        raise HTTPException(status_code=409, detail="Email is already registered")

    db_user = models.User(
        name=user.name.strip(),
        email=email,
        password=hash_password(user.password),
    )
    if not db_user.name:
        logger.warning("Registration rejected because the name is blank")
        raise HTTPException(status_code=422, detail="Name cannot be blank")

    db.add(db_user)
    try:
        logger.debug("Saving new user record")
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning("Registration rejected after a duplicate email database conflict")
        raise HTTPException(status_code=409, detail="Email is already registered") from None
    except Exception as error:
        logger.error("User registration database write failed (%s)", type(error).__name__)
        raise
    db.refresh(db_user)
    logger.info("User registration succeeded for user_id=%s", db_user.id)
    return db_user


@router.post("/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Verify account credentials and issue an access token."""
    logger.info("Login attempt started")
    try:
        user = (
            db.query(models.User)
            .filter(models.User.email == str(credentials.email).lower())
            .first()
        )
    except Exception as error:
        logger.error("Login account lookup failed (%s)", type(error).__name__)
        raise
    if user is None or not verify_password(credentials.password, user.password):
        logger.warning("Login rejected because the credentials were invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id, user.auth_version)
    logger.info("Login succeeded for user_id=%s", user.id)
    return schemas.TokenResponse(access_token=token)


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """Return the profile associated with the current bearer token."""
    logger.debug("Returning profile for user_id=%s", current_user.id)
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Invalidate existing access tokens for the current user."""
    logger.info("Logout started for user_id=%s", current_user.id)
    current_user.auth_version += 1
    try:
        db.commit()
    except Exception as error:
        logger.error("Logout database update failed (%s)", type(error).__name__)
        raise
    logger.info("Logout completed for user_id=%s", current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)