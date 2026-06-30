import asyncio
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the test database module directly
from app.database_test import init_db, engine

async def test():
    await init_db()
    print("init_db OK!")

asyncio.run(test())