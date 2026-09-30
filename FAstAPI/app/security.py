import os
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app import models
from app.database import get_db


# Load local secrets without ever writing their values to the logs.
logger = logging.getLogger(__name__)
load_dotenv(Path(__file__).with_name(".env"))

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
    logger.error("JWT signing key is missing or shorter than 32 characters")
    raise RuntimeError("Set JWT_SECRET_KEY to a random value of at least 32 characters")
logger.debug("JWT signing key is configured")

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    logger.debug("Hashing a password")
    hashed_password = password_hash.hash(password)
    logger.debug("Password hash created")
    return hashed_password


def verify_password(password: str, hashed_password: str) -> bool:
    logger.debug("Checking password credentials")
    is_valid = password_hash.verify(password, hashed_password)
    logger.debug("Password check completed; valid=%s", is_valid)
    return is_valid


def create_access_token(user_id: int, auth_version: int) -> str:
    logger.debug("Creating access token for user_id=%s", user_id)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "ver": auth_version,
        "iat": now,
        "exp": now + timedelta(minutes=30),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    logger.debug("Access token created for user_id=%s", user_id)
    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    logger.debug("Validating bearer authentication")
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        logger.warning("Protected request did not include a bearer token")
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
        )
        user_id = int(payload["sub"])
        auth_version = int(payload["ver"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as error:
        logger.warning("Bearer token validation failed (%s)", type(error).__name__)
        raise unauthorized from None

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None or user.auth_version != auth_version:
        logger.warning("Authentication rejected for user_id=%s", user_id)
        raise unauthorized
    logger.info("Authenticated request for user_id=%s", user_id)
    return user