import logging
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from getenv import load_dotenv

# Keep database startup and session messages easy to find during local debugging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


Database_url = os.getenv("DATABASE_URL")


# Create one engine for the application and check that PostgreSQL is reachable.
logger.info("Starting database connection...")

try:
    engine = create_engine(Database_url)

    # Test the database connection
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    logger.info("Database connection successful!")

except Exception as e:
    logger.error("Database connection failed (%s)", type(e).__name__)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """Provide one database session to a request and always close it afterward."""
    logger.debug("Opening database session")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")


# All SQLAlchemy models inherit from this shared declarative base.
Base = declarative_base()

