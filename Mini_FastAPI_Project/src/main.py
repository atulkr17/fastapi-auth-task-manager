from fastapi import FastAPI

from src.router.user import router as user_router
from src.router.auth import router as auth_router

app = FastAPI(
    title="Mini FastAPI Project",
)


app.include_router(user_router)
app.include_router(auth_router)