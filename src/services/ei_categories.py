from src.repositories.expense_income_categories import (
    ExpenseIncomeCategoriesRepository)
from src.schemas.categories import ExpenseIncomeRead
from src.services.categories import CategoriesService
from src.utils.enum_classes import CategoryGroup
from src.utils.unit_of_work import IUnitOfWork
from src.utils.utils import get_start_month_date


class ExpenseIncomeService(CategoriesService):
    repository = ExpenseIncomeCategoriesRepository
    schema_read = ExpenseIncomeRead

    async def get_all(self, uow: IUnitOfWork, **filters):
        async with uow:
            categories = await self.repository.find_all(**filters)

            for category in categories:
                if category.group == CategoryGroup.expense:
                    category.amount = await uow.transactions.calc_sum(
                        date_from=get_start_month_date(),
                        id_category_to=category.id
                    )
                else:
                    category.amount = await uow.transactions.calc_sum(
                        date_from=get_start_month_date(),
                        id_category_from=category.id
                    )

            return [
                self.schema_read.model_validate(category, from_attributes=True)
                for category in categories]
