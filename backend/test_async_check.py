import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def test():
    engine = create_async_engine("sqlite+aiosqlite:///test_check.db")
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: None)
    print("Async engine OK!")
    await engine.dispose()

asyncio.run(test())