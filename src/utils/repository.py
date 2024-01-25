from abc import ABC, abstractmethod

from sqlalchemy import insert, update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, user_id: int, data: dict):
        raise NotImplemented

    @abstractmethod
    async def find_all(self):
        raise NotImplemented


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, user_id: int, data: dict):
        stmt = (insert(self.model).values(user_id=user_id, **data)
                .returning(self.model))
        res = await self.session.execute(stmt)
        return res.scalar_one().to_read_model()

    async def edit_one(self, id: int, **data):
        stmt = (update(self.model).values(**data).filter_by(id=id)
                .returning(self.model))
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def find_one(self, order_by=None, **filters):
        query = select(self.model).filter_by(**filters)
        if order_by:
            query = query.order_by(order_by)
        res = await self.session.execute(query)
        res = res.scalar_one().to_read_model()
        return res.scalar_one()

    async def find_all(self, **filters) -> list:
        query = select(self.model).filter_by(**filters)
        res = await self.session.execute(query)
        res = [row[0].to_read_model() for row in res.all()]
        return res

    async def drop_one(self, **filters):
        stmt = delete(self.model).filter_by(**filters).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one().to_read_model()

    async def drop_several(self, **filters):
        stmt = delete(self.model).filter_by(**filters).returning(self.model)
        res = await self.session.execute(stmt)
        return [row[0].to_read_model() for row in res.all()]
