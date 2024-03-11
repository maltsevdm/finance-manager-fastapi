import datetime

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import coalesce

from src.db.database import async_session
from src.db.models import Transaction, ExpenseIncomeCategory
from src.repositories.expense_income_categories import (
    ExpenseIncomeCategoriesRepository)
from src.repositories.transations import TransactionsRepository
from src.schemas.categories import ExpenseIncomeRead, ExpenseIncomeAdd
from src.services.categories import CategoriesService
from src.utils.unit_of_work import IUnitOfWork
from src.utils.utils import get_start_month_date


class ExpenseIncomeService(CategoriesService):
    repository = ExpenseIncomeCategoriesRepository
    schema_read = ExpenseIncomeRead

    async def get_all(
            self,
            uow: IUnitOfWork,
            user_id: int,
            date_from: datetime.date | None = None,
            date_to: datetime.date | None = None,
            group=None,
            **kwargs
    ):
        async with async_session() as session:
            t = aliased(Transaction)
            eic = aliased(ExpenseIncomeCategory)
            subq = select(t.destination_id.label('id'),
                          func.sum(t.amount).label('amount'))

            if date_from is not None:
                subq = subq.filter(t.date >= date_from)

            if date_to is not None:
                subq = subq.filter(t.date <= date_to)

            subq = (subq.filter_by(user_id=user_id).
                    group_by(t.destination_id).subquery())

            query = (
                select(
                    eic.id,
                    eic.user_id,
                    eic.name,
                    eic.group,
                    eic.icon,
                    eic.position,
                    eic.monthly_limit,
                    coalesce(subq.c.amount, 0).label('amount')
                )
                .join(subq, eic.id == subq.c.id, isouter=True)
                .filter(eic.user_id == user_id)
            )

            if group is not None:
                query = query.filter(eic.group == group)

            res = await session.execute(query)
            categories = res.all()

            return [
                self.schema_read.model_validate(category, from_attributes=True)
                for category in categories]

    async def add_one(
            self, uow: IUnitOfWork, user_id: int,
            category: ExpenseIncomeAdd
    ):
        async with async_session() as session:
            category_dict = category.model_dump()
            category_dict['user_id'] = user_id

            db_category = await self.repository(session).add_one(category_dict)
            await session.commit()

            db_category.amount = 0
            res = self.schema_read.model_validate(db_category,
                                                  from_attributes=True)
            return res

    async def update_one(
            self, uow: IUnitOfWork, id: int, user_id: int,
            category: BaseModel
    ):
        async with async_session() as session:
            db_category = await self.repository(session).edit_one(
                id=id, user_id=user_id, data=category.model_dump())
            await session.commit()

            db_category.amount = await TransactionsRepository(session).calc_sum(
                date_from=get_start_month_date(),
                destination_id=db_category.id
            )

            return self.schema_read.model_validate(db_category,
                                                   from_attributes=True)

    async def remove_one(
            self, uow: IUnitOfWork, user_id: int, category_id: int
    ):
        async with async_session() as session:
            db_category = await self.repository(session).drop_one(
                id=category_id, user_id=user_id)

            await session.commit()

            db_category.amount = await TransactionsRepository(session).calc_sum(
                date_from=get_start_month_date(),
                destination_id=db_category.id
            )

            return self.schema_read.model_validate(db_category,
                                                   from_attributes=True)
