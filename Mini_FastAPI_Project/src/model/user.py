from sqlalchemy import Column, Integer, String , Boolean, DateTime
#from time import datatime 
from src.db_services.connect_db import logger , Base
from datetime import datetime
logger.info("Creating SQLAlchemy database model for users table")


class USERS(Base):
    __tablename__  = "users"

    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    name = Column(String(25), nullable=False, unique=True)
    email = Column(String(25), nullable = False , unique=True)
    #phone = Column(String(25), nullable = False , unique=True)
    password = Column(String(25), nullable = False )
    medialname = Column(String(25), nullable = True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column( DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
       
        
        
 
    

    