"""
E2E test server - patches the database to use SQLite BEFORE any app imports.
This must be the first import in the chain.
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Step 1: Override the DATABASE_URL environment variable BEFORE importing app modules
# This way, when app.database creates the engine, it uses SQLite instead
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{os.path.abspath('test_e2e.db')}"

# Step 2: Now import the app modules - they'll use the SQLite URL
from app.database import Base, engine, async_session, get_db
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.task import Task

# Step 3: Create tables
import asyncio

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# Initialize DB
asyncio.run(init_db())
print("DB initialized with SQLite")

# Step 4: Create the FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, projects, tasks, analytics

app = FastAPI(title="PMS E2E Test Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    await reset_db()
    return {"status": "reset"}


@app.post("/test/set-role")
async def set_role(data: dict):
    from sqlalchemy import select
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