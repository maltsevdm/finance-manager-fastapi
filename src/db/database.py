from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    async_sessionmaker, create_async_engine, AsyncSession)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

SQLALCHEMY_DATABASE_URL = settings.DB_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
async_session = async_sessionmaker(autocommit=False, autoflush=False,
                                   bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
