import datetime
from typing import Optional, Union

from sqlalchemy import select, func, update

from src.db.models import Transaction
from src.utils.enum_classes import TransactionGroup, TransactionStatus
from src.utils.repository import SQLAlchemyRepository


class TransactionsRepository(SQLAlchemyRepository):
    model = Transaction

    async def calc_sum(
            self,
            id: int | None = None,
            user_id: int | None = None,
            bank_id: int | None = None,
            destination_id: int | None = None,
            group: TransactionGroup | None = None,
            date_from: Optional[datetime.date] = None,
            date_to: Optional[datetime.date] = None,
    ) -> Union[float, int]:
        filters = {
            'id': id,
            'user_id': user_id,
            'group': group,
            'bank_id': bank_id,
            'destination_id': destination_id
        }
        filters = dict(filter(lambda x: x[1] is not None, filters.items()))

        query = select(func.sum(self.model.amount)).filter_by(**filters)
        if date_from:
            query = query.filter(self.model.date >= date_from)
        if date_to:
            query = query.filter(self.model.date <= date_to)
        result = await self.session.execute(query)
        result = result.scalar_one()
        return result if result else 0

    async def find_all_between_dates(
            self, date_from: datetime.date, date_to: datetime.date,
            limit: int, offset: int, **filters
    ):
        query = (select(self.model).filter_by(**filters)
                 .filter(self.model.date.between(date_from, date_to))
                 .limit(limit).offset(offset))
        res = await self.session.execute(query)
        return res.scalars().all()

    async def update_predict_transactions(self):
        stmt = (update(self.model)
                .values(status=TransactionStatus.was_predict)
                .filter_by(date=datetime.date.today(),
                           status=TransactionStatus.predict)
                .returning(self.model))
        res = await self.session.execute(stmt)
        return res.scalars().all()

