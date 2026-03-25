from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings

_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def create_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(settings.database_url, pool_pre_ping=True, future=True)


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_engine()
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    global _session_maker
    if _session_maker is None:
        _session_maker = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_maker


@asynccontextmanager
async def get_async_session() -> AsyncIterator[AsyncSession]:
    session_maker = get_session_maker()
    async with session_maker() as session:
        yield session
