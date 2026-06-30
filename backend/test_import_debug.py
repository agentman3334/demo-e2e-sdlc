"""Minimal test to find the greenlet-breaking import."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def test():
    engine = create_async_engine("sqlite+aiosqlite:///test_minimal.db")
    async with engine.begin() as conn:
        await conn.run_sync(lambda s: None)
    print("OK!")
    await engine.dispose()

# Test 1: No extra imports
print("Test 1: No extra imports")
asyncio.run(test())

# Test 2: Import passlib
print("Test 2: After passlib import")
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
asyncio.run(test())

# Test 3: Import jose
print("Test 3: After jose import")
from jose import jwt
asyncio.run(test())

# Test 4: Import pydantic
print("Test 4: After pydantic import")
from pydantic import BaseModel
asyncio.run(test())

# Test 5: Import fastapi
print("Test 5: After fastapi import")
from fastapi import FastAPI
asyncio.run(test())

# Test 6: Import uvicorn
print("Test 6: After uvicorn import")
import uvicorn
asyncio.run(test())

print("\nAll tests passed!")