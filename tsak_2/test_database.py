import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from database import Task, TaskManager


class TaskManagerTests(unittest.TestCase):
    def setUp(self):
        self.connection = MagicMock()
        self.cursor = self.connection.cursor.return_value.__enter__.return_value
        self.manager = TaskManager(self.connection)
        self.cursor.reset_mock()
        self.connection.commit.reset_mock()

    def test_add_task_returns_created_task(self):
        self.cursor.fetchone.return_value = {
            "id": 7,
            "title": "Review",
            "description": "Read notes",
            "priority": "high",
            "due_date": datetime(2026, 10, 2),
            "status": "pending",
            "created_at": datetime(2026, 10, 1, 12, 0),
        }

        task = self.manager.add_task(" Review ", "Read notes", "high")

        self.assertEqual(
            task,
            Task(
                7,
                "Review",
                "Read notes",
                "high",
                datetime(2026, 10, 2),
                "pending",
                datetime(2026, 10, 1, 12, 0),
            ),
        )
        self.assertIn("INSERT INTO task_manager", self.cursor.execute.call_args.args[0])
        self.assertIn("COALESCE(%s, CURRENT_TIMESTAMP)", self.cursor.execute.call_args.args[0])
        self.assertEqual(self.cursor.execute.call_args.args[1], ("Review", "Read notes", "high", None))
        self.connection.commit.assert_called_once()

    def test_manager_does_not_create_or_modify_tables_on_init(self):
        self.cursor.execute.assert_not_called()
        self.connection.commit.assert_not_called()

    def test_update_builds_assignments_only_from_allowed_fields(self):
        self.cursor.fetchone.return_value = {
            "id": 2,
            "title": "Updated",
            "description": None,
            "priority": "medium",
            "due_date": None,
            "status": "pending",
            "created_at": datetime(2026, 10, 1, 12, 0),
        }

        task = self.manager.update_task(2, title="Updated")

        self.assertEqual(task.title, "Updated")
        self.assertIn("title = %s", self.cursor.execute.call_args.args[0])
        self.assertEqual(self.cursor.execute.call_args.args[1], ("Updated", 2))
        with self.assertRaises(ValueError):
            self.manager.update_task(2, id=99)

    def test_filter_search_and_statistics_use_parameterized_queries(self):
        self.cursor.fetchall.side_effect = [[], [], [("pending", 3)]]

        self.assertEqual(self.manager.filter_tasks("pending", "high"), [])
        self.assertEqual(self.cursor.execute.call_args.args[1], ["pending", "high"])
        self.assertEqual(self.manager.search_tasks("plan"), [])
        self.assertEqual(self.cursor.execute.call_args.args[1], ("%plan%",))
        self.assertEqual(self.manager.get_statistics(2), {"pending": 3})
        query, parameters = self.cursor.execute.call_args.args
        self.assertIn("GROUP BY status HAVING COUNT(*) >= %s", query)
        self.assertEqual(parameters, (2,))

    def test_delete_reports_if_a_task_was_removed(self):
        self.cursor.rowcount = 1
        self.assertTrue(self.manager.delete_task(4))
        self.cursor.execute.assert_called_once_with(
            "DELETE FROM task_manager WHERE id = %s", (4,)
        )

    def test_export_writes_json(self):
        self.manager.get_tasks = MagicMock(
            return_value=[
                Task(
                    1,
                    "Plan",
                    None,
                    "low",
                    datetime(2026, 10, 3),
                    "pending",
                    datetime(2026, 10, 1, 12, 0),
                )
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "tasks.json"
            json_output = self.manager.export_json(output)
            data = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(data[0]["title"], "Plan")
        self.assertEqual(data[0]["due_date"], "2026-10-03T00:00:00")
        self.assertEqual(data[0]["created_at"], "2026-10-01T12:00:00")
        self.assertEqual(json.loads(json_output), data)
        self.assertIn("\n  {", json_output)


if __name__ == "__main__":
    unittest.main()
