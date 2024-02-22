from abc import ABC, abstractmethod

from sqlalchemy import insert, update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplemented

    @abstractmethod
    async def find_all(self):
        raise NotImplemented


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit_one(self, data: dict, **filters):
        stmt = (update(self.model).values(**data).filter_by(**filters)
                .returning(self.model))
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def find_one(self, **filters):
        query = select(self.model).filter_by(**filters)
        res = await self.session.execute(query)
        return res.scalar_one()

    async def find_all(self, **filters):
        query = select(self.model).filter_by(**filters)
        res = await self.session.execute(query)
        return res.scalars().all()

    async def drop_one(self, **filters):
        stmt = delete(self.model).filter_by(**filters).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def drop_several(self, **filters):
        stmt = delete(self.model).filter_by(**filters).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().all()
