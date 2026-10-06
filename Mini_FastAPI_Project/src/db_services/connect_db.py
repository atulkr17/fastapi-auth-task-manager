from sqlalchemy.orm import sessionmaker , declarative_base
from sqlalchemy import create_engine, text
import os 
from dotenv import load_dotenv
import logging 
load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)


#get the databse details from .env 
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

logger.info(
    "Database configuration loaded: host=%s, port=%s, database=%s, user=%s",
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
)
#Database_url = os.getenv('DATABASE_URL')

logger.info("Creating SQLAlchemy database engine")
engine = create_engine(
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"    
)


#create a database connection
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        




#Check database connection 
try:
    with engine.connect() as connection:
    # connection = engine.connect()
        result = connection.execute(text('SELECT 1'))
        logger.info("Database connection successfully")

    
    print("checking connection is on or off: ", connection) 

except Exception as e:
    logger.info(f'Database connection Failed{e}')
    #print('Error', e)        
