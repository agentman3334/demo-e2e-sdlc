"""FastAPI app configured for E2E testing with SQLite."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database_test import init_db, reset_db
from app.routers import auth, projects, tasks, analytics
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    await init_db()
    yield
    # Shutdown: nothing needed


app = FastAPI(title="PMS E2E Test Server", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(analytics.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/test/reset-db")
async def test_reset_db():
    """Reset the database for E2E testing."""
    await reset_db()
    return {"status": "reset"}