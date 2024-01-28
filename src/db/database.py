from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    async_sessionmaker, create_async_engine, AsyncSession)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

SQLALCHEMY_DATABASE_URL = settings.DB_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session = async_sessionmaker(autocommit=False, autoflush=False,
                                   bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
