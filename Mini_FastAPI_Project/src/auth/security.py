import os
from datetime import datetime, timedelta, timezone

import jwt 
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()


#jwt configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM= os.getenv('JWT_ALGORITHM', "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
      os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
)
# Password hashing object
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    #convart a plain-text password into a secure hashed password
    return password_hash.hash(password)

def verify_password(
        plain_password: str,
        hashed_password: str
) -> bool:
       return password_hash.verify(
             plain_password,
             hashed_password
       )    

def create_access_token(user_id: int, email:str)-> str:
      
      expire = datetime.now(timezone.utc) + timedelta(
            minutes = ACCESS_TOKEN_EXPIRE_MINUTES
      )

      payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire
      }  
      access_token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )  

      return access_token


def create_refresh_token(user_id: int, email: str) -> str:
      #create long-lived refresh token
      expire = (datetime.now(timezone.utc)
                + timedelta(days = REFRESH_TOKEN_EXPIRE_DAYS)
                )

      payload = {
             "sub": str(user_id),
             "email": email,
             "type": "refresh",
             "exp": expire
      }

      refresh_token = jwt.encode(
            payload,
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM
      )

      return refresh_token