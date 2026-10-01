import logging

from database import TaskManager

logger = logging.getLogger(__name__)


def prompt_task(manager: TaskManager) -> None:
    title = input("Title: ").strip()
    description = input("Description: ").strip()
    priority = input("Priority (low/medium/high) [medium]: ").strip().lower() or "medium"
    task = manager.add_task(title, description, priority)
    print(f"Created task #{task.id}: {task.title}")


def print_tasks(tasks: list) -> None:
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        due_date = task.due_date.isoformat() if task.due_date else "-"
        print(f"#{task.id} [{task.status}] {task.title} | {task.priority} | due {due_date}")
        if task.description:
            print(f"  {task.description}")


def run() -> None:
    manager = TaskManager.connect_from_env()
    actions = {
        "1": "Add task",
        "2": "View all tasks",
        "3": "View task by ID",
        "4": "Update task",
        "5": "Delete task",
        "6": "Mark task completed/pending",
        "7": "Filter tasks",
        "8": "Search by title",
        "9": "Task statistics",
        "10": "Export JSON",
        "0": "Exit",
    }
    try:
        while True:
            print("\nTask Manager")
            for key, label in actions.items():
                print(f"{key}. {label}")
            choice = input("Choose an action: ").strip()

            if choice == "0":
                break
            if choice == "1":
                prompt_task(manager)
            elif choice == "2":
                print_tasks(manager.get_tasks())
            elif choice == "3":
                task = manager.get_task(int(input("Task ID: ")))
                print_tasks([task] if task else [])
            elif choice == "4":
                task_id = int(input("Task ID: "))
                fields = {}
                for field in ("title", "description", "priority"):
                    value = input(f"New {field} (blank to keep): ").strip()
                    if value:
                        fields[field] = value
                task = manager.update_task(task_id, **fields)
                print_tasks([task] if task else [])
            elif choice == "5":
                task_id = int(input("Task ID: "))
                print("Task deleted." if manager.delete_task(task_id) else "Task not found.")
            elif choice == "6":
                task_id = int(input("Task ID: "))
                status = input("Status (completed/pending): ").strip().lower()
                task = manager.set_status(task_id, status)
                print_tasks([task] if task else [])
            elif choice == "7":
                status = input("Status (blank for any): ").strip().lower() or None
                priority = input("Priority (blank for any): ").strip().lower() or None
                print_tasks(manager.filter_tasks(status, priority))
            elif choice == "8":
                print_tasks(manager.search_tasks(input("Title contains: ").strip()))
            elif choice == "9":
                for status, count in manager.get_statistics().items():
                    print(f"{status}: {count}")
            elif choice == "10":
                path = input("Export path [tasks.json]: ").strip() or "tasks.json"
                json_data = manager.export_json(path)
                print(json_data)
                print(f"Exported tasks to {path}")
            else:
                print("Choose one of the listed actions.")
    except (ValueError, RuntimeError) as error:
        logger.warning("Invalid input or configuration: %s", error)
        print(f"Error: {error}")
    except Exception:
        logger.exception("Task manager operation failed")
        print("An unexpected error occurred; see the log for details.")
    finally:
        manager.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run()
