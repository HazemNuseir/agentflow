import asyncio
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

Base = declarative_base()

sync_url = settings.DATABASE_URL.replace("+aiosqlite", "").replace("postgresql+asyncpg://", "postgresql+psycopg://").replace("postgresql://", "postgresql+psycopg://")
connect_args = {"check_same_thread": False} if sync_url.startswith("sqlite:") else {}
engine = create_engine(sync_url, connect_args=connect_args, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class AsyncSessionShim:
    """
    Direct zero-overhead async coroutine adapter over SQLAlchemy sessions.
    Executes in-process SQLite without threadpool deadlocks on Python 3.14.
    """
    def __init__(self):
        self.session = SyncSessionLocal()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        self.session.close()

    async def execute(self, statement: Any):
        return self.session.execute(statement)

    async def commit(self):
        self.session.commit()

    async def flush(self):
        self.session.flush()

    async def rollback(self):
        self.session.rollback()

    async def close(self):
        self.session.close()

    def add(self, instance: Any):
        self.session.add(instance)

    async def delete(self, instance: Any):
        self.session.delete(instance)

    async def get(self, entity: Any, ident: Any):
        return self.session.get(entity, ident)

def AsyncSessionLocal():
    return AsyncSessionShim()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    import database.models
    Base.metadata.create_all(engine)
