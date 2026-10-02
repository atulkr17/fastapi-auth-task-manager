# FastAPI Setup

This project is a simple FastAPI application for managing users.

## Project Structure

- `app/main.py` - FastAPI application entry point
- `app/crud.py` - CRUD routes for users
- `app/database.py` - Database connection and session setup
- `app/modal.py` - SQLAlchemy ORM model
- `app/schems.py` - Pydantic request/response schemas
- `app/.env` - Environment variables (including `DATABASE_URL`)

## Requirements

Install the project dependencies using:

```bash
uv pip install fastapi uvicorn sqlalchemy python-dotenv
```

## Run the app

From the project root:

```bash
cd FastAPIsetup
uv run python app/main.py
```

Or directly from the app folder:

```bash
cd FastAPIsetup/app
uv run python main.py
```

Then open Swagger UI in your browser:

```text
http://127.0.0.1:8000/docs
```

## Available endpoints

- `GET /main/users` - Get all users
- `POST /main/create_user` - Create a user
- `GET /main/users/{user_id}` - Get a user by ID
- `PUT /main/users/{user_id}` - Update a user
- `DELETE /main/users/{user_id}` - Delete a user

## Environment

Make sure your `.env` file contains a valid PostgreSQL connection string:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/your_database
```
