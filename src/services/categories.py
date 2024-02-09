from fastapi.openapi.models import Schema

from src.schemas.categories import (
    ExpenseIncomeAdd, ExpenseIncomeRead, BankAdd, BankRead, CategoryUpdate)
from src.utils.enum_classes import CategoryGroup, ExpenseIncomeGroup, BankGroup
from src.utils.unit_of_work import IUnitOfWork
from src.utils.utils import get_start_month_date


class CategoriesService:
    def _get_category_schema(
            self, group: CategoryGroup | ExpenseIncomeGroup | BankGroup
    ) -> Schema:
        if group == CategoryGroup.bank:
            return BankRead
        else:
            return ExpenseIncomeRead

    async def get_categories(self, uow: IUnitOfWork, **filters):
        async with uow:
            categories = await uow.categories.find_all(**filters)

            for category in categories:
                if category.group == CategoryGroup.expense:
                    category.amount = await uow.transactions.calc_sum(
                        date_from=get_start_month_date(),
                        id_category_to=category.id
                    )
                elif category.group == CategoryGroup.income:
                    category.amount = await uow.transactions.calc_sum(
                        date_from=get_start_month_date(),
                        id_category_from=category.id
                    )

            res = []
            for category in categories:
                schema = self._get_category_schema(category.group)
                res.append(
                    schema.model_validate(category, from_attributes=True))

            return res

    async def add_one(
            self, uow: IUnitOfWork, user_id: int, group: CategoryGroup,
            category: ExpenseIncomeAdd | BankAdd
    ):
        category_dict = category.model_dump()
        async with uow:
            position = await uow.categories.define_position(user_id,
                                                            category.group)
            category_dict['group'] = group
            category_dict['position'] = position
            category_dict['user_id'] = user_id
            db_category = await uow.categories.add_one(category_dict)

            await uow.commit()
            schema = self._get_category_schema(db_category.group)
            res = schema.model_validate(db_category, from_attributes=True)
            return res

    async def update_one(
            self, uow: IUnitOfWork, id: int, user_id: int,
            category: CategoryUpdate
    ):
        async with uow:
            db_category = await uow.categories.edit_one(
                id=id, user_id=user_id, data=category.model_dump())
            await uow.commit()

            schema = self._get_category_schema(db_category.group)
            return schema.model_validate(db_category, from_attributes=True)


async def remove_one(
        self, uow: IUnitOfWork, user_id: int, category_id: int
):
    async with uow:
        db_category = await uow.categories.drop_one(
            id=category_id, user_id=user_id)
        await uow.categories.update_positions(
            user_id=user_id, group=db_category.group, new_position=1000,
            old_position=db_category.position
        )
        await uow.commit()

        schema = self._get_category_schema(db_category.group)
        return schema.model_validate(db_category, from_attributes=True)
