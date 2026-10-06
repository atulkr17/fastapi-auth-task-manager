from fastapi import FastAPI, Depends, HTTPException, status ,  APIRouter
from sqlalchemy.orm import Session
from src.db_services.connect_db import logger
from src.auth.security import (
    create_access_token,
    verify_password
)

from src.crud.user import(
    create_user,
    get_user_by_email
)

from src.crud.user import(
    create_user,
    get_user_by_email
)

from src.db_services.connect_db import get_db


from src.schemas.user import(
    UserSignup,
    UserSignin,
    TokenResponse
)

router = APIRouter(prefix = "/auth", tags  = ["Authentication"])

@router.post(
    "/signup",
    status_code= status.HTTP_201_CREATED
)
def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    """Register a new user"""

    # check wheather email already exict
    existing_user = get_user_by_email(db, user_data.email)
    print(existing_user)

    if existing_user:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail =" Email already registered")
    #create new user
    user = create_user(
        db = db,
        name = user_data.name,
        email = user_data.email,
        password = user_data.password,
        #medialname = user_data.medialname
     )
    
    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email
    }

#SIGN IN

@router.post(
    "/signin", response_model = TokenResponse
)
def signin(user_data: UserSignin, db: Session = Depends(get_db)):
     """
    Sign in an existing user and generate
    JWT access token.
    """
     #find User by email
     logger.info("user is start fatching")
     user = get_user_by_email(
         db,
         user_data.email
     )
     
      # User does not exist
     if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

     #verify password
     password_valid = verify_password(user_data.password, user.password)

     if not password_valid:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"

        )
     access_token = create_access_token(
        user_id=user.id,
        email=user.email
    )
     return {
        "access_token": access_token,
        "token_type": "bearer"
    }