import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Task:
    id: int
    title: str
    description: str | None
    priority: str
    due_date: datetime | None
    status: str
    created_at: datetime | None


class TaskManager:
    """PostgreSQL-backed task operations."""

    def __init__(self, connection: Any):
        self.connection = connection

    @classmethod
    def connect_from_env(cls) -> "TaskManager":
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("Set DATABASE_URL before starting the task manager.")
        return cls(psycopg2.connect(database_url))

    @staticmethod
    def _task(row: dict[str, Any] | None) -> Task | None:
        return Task(**row) if row else None

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: datetime | None = None,
    ) -> Task:
        self._validate_fields({"title": title, "priority": priority})
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # PostgreSQL supplies id and created_at; the query supplies today's due_date.
            cursor.execute(
                """INSERT INTO task_manager (title, description, priority, due_date)
                   VALUES (%s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP)) RETURNING *""",
                (title.strip(), description, priority, due_date),
            )
            task = self._task(cursor.fetchone())
        self.connection.commit()
        logger.info("Created task %s", task.id)
        return task

    def get_tasks(self) -> list[Task]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM task_manager ORDER BY id")
            return [Task(**row) for row in cursor.fetchall()]

    def get_task(self, task_id: int) -> Task | None:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM task_manager WHERE id = %s", (task_id,))
            return self._task(cursor.fetchone())

    def update_task(self, task_id: int, **fields: Any) -> Task | None:
        allowed = {"title", "description", "priority", "status"}
        unknown = fields.keys() - allowed
        logger.debug("Updating task %s with fields: %s", unknown, fields)   
        if unknown:
            raise ValueError(f"Unknown task fields: {', '.join(sorted(unknown))}")
        if not fields:
            return self.get_task(task_id)
        self._validate_fields(fields)
        assignments = ", ".join(f"{field} = %s" for field in fields)
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                f"UPDATE task_manager SET {assignments} WHERE id = %s RETURNING *",
                (*fields.values(), task_id),
            )
            task = self._task(cursor.fetchone())
        self.connection.commit()
        if task:
            logger.info("Updated task %s", task_id)
        return task

    def delete_task(self, task_id: int) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM task_manager WHERE id = %s", (task_id,))
            deleted = cursor.rowcount > 0
        self.connection.commit()
        if deleted:
            logger.info("Deleted task %s", task_id)
        return deleted

    def set_status(self, task_id: int, status: str) -> Task | None:
        return self.update_task(task_id, status=status)

    def filter_tasks(
        self, status: str | None = None, priority: str | None = None
    ) -> list[Task]:
        conditions = []
        values = []
        if status:
            self._validate_fields({"status": status})
            conditions.append("status = %s")
            values.append(status)
        if priority:
            self._validate_fields({"priority": priority})
            conditions.append("priority = %s")
            values.append(priority)
        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT * FROM task_manager{where} ORDER BY id", values)
            return [Task(**row) for row in cursor.fetchall()]

    def search_tasks(self, title: str) -> list[Task]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM task_manager WHERE title ILIKE %s ORDER BY id",
                (f"%{title}%",),
            )
            return [Task(**row) for row in cursor.fetchall()]

    def get_statistics(self, minimum_count: int = 0) -> dict[str, int]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT status, COUNT(*) AS task_count FROM task_manager
                   GROUP BY status HAVING COUNT(*) >= %s ORDER BY status""",
                (minimum_count,),
            )
            return dict(cursor.fetchall())

    def export_json(self, path: str | Path) -> str:
        tasks = [asdict(task) for task in self.get_tasks()]
        # ISO strings make Python date and datetime values valid JSON values.
        json_data = json.dumps(tasks, indent=2, default=lambda value: value.isoformat())
        Path(path).write_text(json_data, encoding="utf-8")
        logger.info("Exported %d tasks to %s", len(tasks), path)
        return json_data

    @staticmethod
    def _validate_fields(fields: dict[str, Any]) -> None:
        if "title" in fields and (not isinstance(fields["title"], str) or not fields["title"].strip()):
            raise ValueError("Title must not be empty.")
        if "priority" in fields and fields["priority"] not in {"low", "medium", "high"}:
            raise ValueError("Priority must be low, medium, or high.")
        if "status" in fields and fields["status"] not in {"pending", "completed"}:
            raise ValueError("Status must be pending or completed.")

    def close(self) -> None:
        self.connection.close()
