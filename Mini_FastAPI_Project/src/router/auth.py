from fastapi import FastAPI, Depends, HTTPException, status ,  APIRouter
from sqlalchemy.orm import Session
from src.db_services.connect_db import logger
from src.auth.security import (
    create_access_token,
    verify_password
)
import os
import jwt
#jwt configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM= os.getenv('JWT_ALGORITHM', "HS256")
from src.crud.user import(
    create_user,
    get_user_by_email
)
from src.auth.security import (
    create_access_token,
    create_refresh_token,
    verify_password
)
from src.crud.user import(
    create_user,
    get_user_by_email
)

from src.db_services.connect_db import get_db


from src.schemas.user import(
    UserSignup,
    UserSignin,
    TokenResponse,
    RefreshTokenRequest
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
     logger.info("Fatching user by email")
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
     #create refresh token
     refresh_token = create_refresh_token(user_id = user.id, email = user.email) 
     print("refresh token generated success full")
     return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model = TokenResponse)
def refresh_access_token(token_data: RefreshTokenRequest):
    # Generate a new access token using a valid refresh token
    try: #decode refresh token
        payload = jwt.decode(
            token_data.refresh_token,
            JWT_SECRET_KEY,
            algorithms = [JWT_ALGORITHM]
        )
        #get token type
        token_type = payload.get("type")

        #Make sure this is a refresh token
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid refresh token"
            )
        #get user information 
        user_id= payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid refresh token"
            )
        #Generate new access token
        new_access_token = create_access_token(
            user_id=int(user_id),
            email=email
        )

        return{
            "access_token": new_access_token,
            "refresh_token": token_data.refresh_token,
            "token_type":"bearer"
        }

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
