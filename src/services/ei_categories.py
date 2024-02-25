from pydantic import BaseModel

from src.db.database import async_session
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

    async def get_all(self, uow: IUnitOfWork, **filters):
        async with async_session() as session:
            categories = await self.repository(session).find_all(**filters)

            for category in categories:
                category.amount = await TransactionsRepository(
                    session).calc_sum(
                    date_from=get_start_month_date(),
                    destination_id=category.id
                )

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
