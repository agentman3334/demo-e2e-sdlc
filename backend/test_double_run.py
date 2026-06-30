import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def test():
    engine = create_async_engine("sqlite+aiosqlite:///test_minimal.db")
    async with engine.begin() as conn:
        await conn.run_sync(lambda s: None)
    print("OK!")
    await engine.dispose()

# First call
print("First asyncio.run()...")
asyncio.run(test())
print("First call done!")

# Second call
print("Second asyncio.run()...")
asyncio.run(test())
print("Second call done!")