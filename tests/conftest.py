import asyncio
from typing import AsyncGenerator

import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, \
    AsyncSession
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app
from src.config import settings
from src.db.database import get_async_session
from src import Base

DATABASE_URL_TEST = settings.DB_URL

engine_test = create_async_engine(DATABASE_URL_TEST, echo=False)
async_session_maker = async_sessionmaker(autocommit=False, autoflush=False,
                                         bind=engine_test,
                                         expire_on_commit=False)

Base.metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session
client = TestClient(app)


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    assert settings.MODE == 'TEST'
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test",
                           follow_redirects=True) as ac:
        yield ac
