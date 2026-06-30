import sys, os, asyncio
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app.database as db_module
from app.database_test import get_db as get_test_db, reset_db, init_db, engine
db_module.get_db = get_test_db

from app.routers import auth, projects, tasks, analytics
print("All routers imported OK")

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

# Initialize DB before starting server
asyncio.run(init_db())
print("DB initialized")

import uvicorn
print("Starting server...")
uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")