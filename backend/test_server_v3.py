import sys, os, asyncio
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Step 1: Import database_test directly (without importing app.database first)
from app.database_test import init_db, engine
print("Step 1: database_test imported")

# Step 2: Try init_db BEFORE importing routers
asyncio.run(init_db())
print("Step 2: init_db succeeded")

# Step 3: Now import routers
import app.database as db_module
from app.database_test import get_db as get_test_db
db_module.get_db = get_test_db

from app.routers import auth, projects, tasks, analytics
print("Step 3: routers imported")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PMS E2E Test")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.dependency_overrides[db_module.get_db] = get_test_db
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(analytics.router)

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/test/reset-db")
async def test_reset():
    from app.database_test import reset_db
    await reset_db()
    return {"status": "reset"}

@app.post("/test/set-role")
async def set_role(data: dict):
    from sqlalchemy import select
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

import uvicorn
print("Starting server...")
uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")