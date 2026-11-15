import os
import sys

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "api")))

from database.session import AsyncSessionLocal
from database.models import User
from sqlalchemy import select

def run_sync(coro):
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value
    raise RuntimeError("Coroutine suspended unexpectedly")

async def test_db():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User))
        users = res.scalars().all()
        return len(users)

count = run_sync(test_db())
print("USER COUNT IN DB:", count)
