import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/api")))

import httpx
from main import app

async def main():
    print("Initializing client without context manager...", flush=True)
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")
    print("Sending GET /health...", flush=True)
    r = await client.get("/health")
    print("Response received:", r.status_code, r.json(), flush=True)
    await client.aclose()
    print("Done cleanly!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
