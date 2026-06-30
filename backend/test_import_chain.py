import sys, os, asyncio
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test importing app.database
import app.database as db_module
print("app.database imported OK")

from app.database_test import get_db as get_test_db, reset_db, init_db, engine
print("database_test imported OK")

db_module.get_db = get_test_db
print("get_db patched OK")

# Now try init_db
asyncio.run(init_db())
print("init_db OK after patching")