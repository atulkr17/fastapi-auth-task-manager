import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv(Path(__file__).with_name(".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL is not set in the .env file")

logger.info("Starting database connection...")
engine = create_engine(database_url)

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    logger.info("Database connection successful!")
except Exception as exc:
    logger.error("Database connection failed (%s)", type(exc).__name__)
    raise

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Provide one database session to a request and always close it afterward."""
    logger.debug("Opening database session")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")