"""E2E test server - patches the FastAPI app to use SQLite instead of PostgreSQL."""
import sys
import os
import asyncio

# Patch the database module BEFORE importing routers
import app.database as db_module
from app.database_test import get_db as get_test_db, reset_db, init_db, engine

# Override the get_db dependency
db_module.get_db = get_test_db
db_module.async_session = db_module.async_session  # keep reference but we won't use it

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

# Override the dependency at the app level
from app.database_test import async_session as test_async_session
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)