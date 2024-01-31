import asyncio
import sys
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app
from src.config import settings
from src.db.database import engine
from src import Base


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

client = TestClient(app)

@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    assert settings.MODE == 'TEST'
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # async with engine_test.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session', autouse=True)
async def register(ac: AsyncClient):
    response = await ac.post("/api/auth/register", json={
        "email": "string",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "string"
    })

    assert response.status_code == 201


@pytest.fixture(scope='session', autouse=False)
async def token(ac: AsyncClient) -> str:
    response = await ac.post(
        'api/auth/jwt/login',
        data={
            'username': 'string',
            'password': 'string'
        },
    )

    assert response.status_code == 204

    cookie = response.headers['set-cookie']
    return cookie.split(';')[0].split('=')[1]


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# @pytest.fixture(scope="session")
# def anyio_backend():
#     return "asyncio"

@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test",
                           follow_redirects=True) as ac:
        yield ac
