import asyncio
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Step 1: Create a PostgreSQL engine (like app.database does)
from sqlalchemy.ext.asyncio import create_async_engine
pg_engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/pms", echo=False)
print("PostgreSQL engine created (not connected)")

# Step 2: Now try to use a SQLite engine
sqlite_engine = create_async_engine("sqlite+aiosqlite:///test_e2e.db")

async def go():
    async with sqlite_engine.begin() as conn:
        await conn.run_sync(lambda s: None)
    print("SQLite engine OK after PG engine creation!")

try:
    asyncio.run(go())
except Exception as e:
    print(f"FAILED: {e}")
    # Try without the PG engine
    pg_engine.dispose()
    sqlite_engine2 = create_async_engine("sqlite+aiosqlite:///test_e2e2.db")
    async def go2():
        async with sqlite_engine2.begin() as conn:
            await conn.run_sync(lambda s: None)
        print("SQLite engine OK after PG engine disposal!")
    asyncio.run(go2())