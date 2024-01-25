from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    async_sessionmaker, create_async_engine, AsyncSession)

from src.db.auth_data import USER, PASS, HOST, PORT, DB

SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg://{USER}:{PASS}@{HOST}:{PORT}/{DB}'

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session = async_sessionmaker(autocommit=False, autoflush=False,
                                   bind=engine, expire_on_commit=False)


def get_db():
    db = async_session()
    try:
        yield db
    finally:
        db.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
