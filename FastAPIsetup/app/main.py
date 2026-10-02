from fastapi import FastAPI
import uvicorn

try:
    from app.crud import router
    from app.database import Base, engine
except ImportError:  # pragma: no cover - allows running main.py directly
    from crud import router
    from database import Base, engine

app = FastAPI(title="FastAPI Setup")

# Ensure the database tables exist before handling requests.
Base.metadata.create_all(bind=engine)

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)