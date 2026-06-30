"""Start the E2E test server with SQLite backend."""
import sys
import os

# Ensure we're in the backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Patch database module BEFORE importing routers
import app.database as db_module
from app.database_test import get_db as get_test_db, reset_db, init_db, engine

# Override the get_db in the database module so routers pick it up
db_module.get_db = get_test_db

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import auth, projects, tasks, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="PMS E2E Test Server", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Also override at app level for dependency injection
app.dependency_overrides[db_module.get_db] = get_test_db

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(analytics.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/test/reset-db")
async def test_reset_db():
    await reset_db()
    return {"status": "reset"}


@app.post("/test/set-role")
async def test_set_role(data: dict):
    """Test helper: Set a user's role. Body: {user_id, role}"""
    from sqlalchemy import select, update
    from app.models.user import User
    from app.database_test import async_session
    async with async_session() as db:
        result = await db.execute(select(User).where(User.id == data["user_id"]))
        user = result.scalar_one_or_none()
        if not user:
            return {"error": "User not found"}
        user.role = data["role"]
        await db.commit()
        return {"user_id": user.id, "role": user.role}


if __name__ == "__main__":
    import uvicorn
    print("Starting E2E test server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")