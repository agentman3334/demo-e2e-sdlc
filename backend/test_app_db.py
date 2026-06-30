import asyncio
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Set env var BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///" + os.path.abspath("test_e2e.db")

# Now import - this should use SQLite
from app.database import Base, engine, async_session, get_db
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.task import Task

async def go():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("App DB init OK!")

asyncio.run(go())