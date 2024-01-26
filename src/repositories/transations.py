import datetime
from typing import Optional, Union

from sqlalchemy import select, func

from src.db.models import Transaction
from src.utils.repository import SQLAlchemyRepository


class TransactionsRepository(SQLAlchemyRepository):
    model = Transaction

    async def calc_sum(
            self,
            date_from: Optional[datetime.date] = None,
            date_to: Optional[datetime.date] = None,
            **filters
    ) -> Union[float, int]:
        query = select(func.sum(self.model.amount)).filter_by(**filters)
        if date_from:
            query = query.filter(self.model.date >= date_from)
        if date_to:
            query = query.filter(self.model.date <= date_to)
        result = await self.session.execute(query)
        result = result.scalar_one()
        return result if result else 0
