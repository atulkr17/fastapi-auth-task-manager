import os

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException,status

from fastapi.security import OAuth2PasswordBearer

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM= os.getenv("JWT_ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer( tokenUrl= "/auth/singin")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Extract and validate JWT token.

    This function will be used as a dependency
    for protected APIs.
    """
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Invalid or expire access token",
        headers={"WW-Authenticate": "Bearer"} 

    ) 

    try:
         payload = jwt.decode(
              token,
              JWT_SECRET_KEY,
              algorithms = [JWT_ALGORITHM]

         )
         user_id = payload.get("sub")
         email = payload.get("email")

         if user_id is None:
              raise credentials_exception

         return {
              "user_id ": int(user_id),
              "email":  email
         }

    except jwt.ExpiredSignatureError:
         raise HTTPException(
              status_code = status.HTTP_401_UNAUTHORIZED,
              detail = "Access token has expired",
              headers = {
                   "www-Authenticate": "Bearer"
              }
         )
    except jwt.InvalideTokenError:
         raise credentials_exception