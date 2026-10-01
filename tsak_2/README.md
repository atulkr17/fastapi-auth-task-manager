# CLI Task Manager

A beginner-friendly command-line task manager backed by PostgreSQL. It supports task CRUD, filtering, searching, statistics, and JSON export.

## Features

- Add, view, update, and delete tasks
- Mark tasks as pending or completed
- Filter by status or priority
- Search task titles
- Show counts grouped by status
- Export tasks as formatted JSON to a file and the terminal
- Store tasks in PostgreSQL

## Project Structure

```text
.
|-- database.py       # Task model and PostgreSQL operations
|-- main.py           # Interactive CLI
|-- requirements.txt  # Python dependencies
|-- test_database.py  # unittest suite
|-- .env              # Local database URL; do not commit
|-- .gitignore        # Ignore rules for local/private files
|-- 1                 # Existing JSON task export
```

## Technologies

- Python 3.10+
- PostgreSQL
- psycopg2
- python-dotenv
- Python `unittest`

## Setup

1. Install Python 3.10 or newer and PostgreSQL.
2. Open PowerShell in this project folder:

   ```powershell
   Set-Location path\to\tsak_2
   ```

3. Create and activate a virtual environment, then install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

## Environment Variables

Create a `.env` file beside `database.py` and add your PostgreSQL connection URL:

```dotenv
DATABASE_URL=postgresql://YOUR_USER:YOUR_URL_ENCODED_PASSWORD@localhost:5432/task_manager_db
```

Replace the placeholders with your own database details. URL-encode special characters in the password (for example, `@` becomes `%40`). Do not commit `.env` or share its contents.

`database.py` loads this file automatically. A `DATABASE_URL` already set in the current PowerShell session takes precedence over the `.env` value.

## Database Setup

The application uses the existing table named `task_manager`. It does not create or alter tables. Create the database and table before starting the CLI. For example, in `psql`, select the intended database and run:

```sql
CREATE TABLE task_manager (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    due_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

The application generates `due_date` using the current timestamp when a task is added without one. PostgreSQL generates `id` and `created_at` from their defaults.

## Run and Test

With the virtual environment active:

```powershell
python main.py
```

Run the unit tests with:

```powershell
python -m unittest -v
```

If you use `uv` and dependencies are installed in its environment, you can run:

```powershell
uv run python main.py
uv run python -m unittest -v
```

## CLI Options

At the menu, choose:

| Option | Action |
| --- | --- |
| `1` | Add a task |
| `2` | View all tasks |
| `3` | View a task by ID |
| `4` | Update title, description, or priority |
| `5` | Delete a task |
| `6` | Mark a task completed or pending |
| `7` | Filter tasks by status and/or priority |
| `8` | Search titles |
| `9` | Show task counts grouped by status |
| `10` | Export JSON to a file and display it |
| `0` | Exit |

Valid priorities are `low`, `medium`, and `high`. Valid statuses are `pending` and `completed`.

## Example

Start the CLI and choose option `1`:

```text
Choose an action: 1
Title: Submit report
Description: Send the final report
Priority (low/medium/high) [medium]: high
Created task #1: Submit report
```

Choose option `2` to view tasks, or option `10` to save and display formatted JSON. The default export filename is `tasks.json`.
