"""SQLite-based database for E2E testing (no PostgreSQL required)."""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_e2e.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=False)

# Enable foreign key support in SQLite
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Create all tables for testing."""
    # Import models to register them with Base metadata
    from app.models.user import User
    from app.models.project import Project, ProjectMember
    from app.models.task import Task
    # Use the Base from app.database (which models reference)
    from app.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def reset_db():
    """Drop and recreate all tables for a clean test run."""
    from app.models.user import User
    from app.models.project import Project, ProjectMember
    from app.models.task import Task
    from app.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
