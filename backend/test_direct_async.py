import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def go():
    engine = create_async_engine("sqlite+aiosqlite:///test_check2.db")
    async with engine.begin() as conn:
        await conn.run_sync(lambda s: None)
    print("Direct async engine OK!")
    await engine.dispose()

asyncio.run(go())