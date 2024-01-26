import datetime
from typing import Optional

from sqlalchemy import select, func, update

from src.db.models import CategoryAmount
from src.utils.repository import SQLAlchemyRepository


class CategoriesAmountRepository(SQLAlchemyRepository):
    model = CategoryAmount

    # async def find_one(self, **filters) -> CategoryAmount:
    #     await super().find_one(**filters)

    async def find_all(self, order_by=None, **filters) -> list[CategoryAmount]:
        await super().find_all(order_by=order_by, **filters)

    async def edit_one(self, data: dict, **filters) -> CategoryAmount:
        stmt = (update(self.model).values(**data).filter_by(**filters)
                .returning(self.model))
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def calc_sum(
            self,
            date_from: Optional[datetime.date] = None,
            date_to: Optional[datetime.date] = None,
            **filters
    ):
        query = (select(func.sum(self.model.amount))
                 .filter_by(**filters))
        if date_from:
            query = query.filter(self.model.date >= date_from)
        if date_to:
            query = query.filter(self.model.date <= date_to)
        res = await self.session.execute(query)
        return res.scalar_one()
