from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_session


@asynccontextmanager
async def lifespan_session() -> AsyncSession:
    session = get_session()
    try:
        yield session
    finally:
        await session.close()


async def get_db() -> AsyncSession:
    async with lifespan_session() as session:
        yield session
