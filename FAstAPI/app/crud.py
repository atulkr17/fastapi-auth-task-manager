import logging

from app import models, schemas
from sqlalchemy.orm import Session
from fastapi import HTTPException


logger = logging.getLogger(__name__)


def get_tasks(db: Session, owner_id: int):
    """Return only the tasks that belong to the signed-in user."""
    logger.debug("Loading tasks for owner_id=%s", owner_id)
    try:
        tasks = db.query(models.Task).filter(models.Task.owner_id == owner_id).all()
        logger.info("Loaded %s tasks for owner_id=%s", len(tasks), owner_id)
        return tasks
    except Exception as e:
        logger.error("Task list query failed (%s)", type(e).__name__)
        raise HTTPException(status_code=500, detail=f"Failed to fetch tasks: {e}")


def _get_task(db: Session, task_id: int, owner_id: int):
    """Find an owned task, treating another user's task as not found."""
    logger.debug("Looking up task_id=%s for owner_id=%s", task_id, owner_id)
    try:
        task = (
            db.query(models.Task)
            .filter(models.Task.id == task_id, models.Task.owner_id == owner_id)
            .first()
        )
    except Exception as error:
        logger.error("Task lookup failed (%s)", type(error).__name__)
        raise
    if task is None:
        logger.warning("Task lookup found no owned task for task_id=%s", task_id)
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def create_task(db: Session, task: schemas.TaskCreate, owner_id: int):
    """Save a new task for its owner and return the database record."""
    logger.info("Creating task for owner_id=%s", owner_id)
    try:
        db_task = models.Task(**task.model_dump(), owner_id=owner_id)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
    except Exception as error:
        logger.error("Task creation failed (%s)", type(error).__name__)
        raise
    logger.info("Created task_id=%s for owner_id=%s", db_task.id, owner_id)
    return db_task


def update_task(db: Session, task_id: int, task: schemas.TaskUpdate, owner_id: int):
    """Replace all editable fields on one of the owner's tasks."""
    logger.info("Replacing task_id=%s for owner_id=%s", task_id, owner_id)
    try:
        db_task = _get_task(db, task_id, owner_id)
        for field, value in task.model_dump().items():
            setattr(db_task, field, value)
        db.commit()
        db.refresh(db_task)
    except Exception as error:
        logger.error("Task replacement failed for task_id=%s (%s)", task_id, type(error).__name__)
        raise
    logger.info("Replaced task_id=%s for owner_id=%s", task_id, owner_id)
    return db_task


def partial_update_task(
    db: Session,
    task_id: int,
    task: schemas.TaskPartialUpdate,
    owner_id: int,
):
    """Update only fields included in the request body."""
    logger.info("Partially updating task_id=%s for owner_id=%s", task_id, owner_id)
    try:
        db_task = _get_task(db, task_id, owner_id)
        for field, value in task.model_dump(exclude_unset=True).items():
            setattr(db_task, field, value)
        db.commit()
        db.refresh(db_task)
    except Exception as error:
        logger.error("Task partial update failed for task_id=%s (%s)", task_id, type(error).__name__)
        raise
    logger.info("Partially updated task_id=%s for owner_id=%s", task_id, owner_id)
    return db_task


def delete_task(db: Session, task_id: int, owner_id: int):
    """Delete one of the owner's tasks."""
    logger.info("Deleting task_id=%s for owner_id=%s", task_id, owner_id)
    try:
        db_task = _get_task(db, task_id, owner_id)
        db.delete(db_task)
        db.commit()
    except Exception as error:
        logger.error("Task deletion failed for task_id=%s (%s)", task_id, type(error).__name__)
        raise
    logger.info("Deleted task_id=%s for owner_id=%s", task_id, owner_id)
    