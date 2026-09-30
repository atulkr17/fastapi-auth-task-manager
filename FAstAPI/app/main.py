import logging
from contextlib import asynccontextmanager

from app import auth, crud, models, schemas
from app.database import Base, engine, get_db
from app.security import get_current_user
from fastapi import Depends, FastAPI, status
from sqlalchemy import text
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create model tables and apply the small task-owner migration at startup."""
    logger.info("Starting database schema setup")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("SQLAlchemy tables are ready")
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS "
                    "owner_id INTEGER REFERENCES users(id)"
                )
            )
            logger.debug("Ensured tasks.owner_id exists")
            connection.execute(
                text("CREATE INDEX IF NOT EXISTS ix_tasks_owner_id ON tasks (owner_id)")
            )
        logger.info("Database schema setup completed")
    except Exception as error:
        logger.error("Database schema setup failed (%s)", type(error).__name__)
        raise
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)


        
@app.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_tasks(db, current_user.id)


@app.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_task(db, task, current_user.id)


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.update_task(db, task_id, task, current_user.id)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    crud.delete_task(db, task_id, current_user.id)


@app.patch("/tasks/{task_id}", response_model=schemas.TaskResponse)
def partial_update_task(
    task_id: int,
    task: schemas.TaskPartialUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.partial_update_task(db, task_id, task, current_user.id)
    
    