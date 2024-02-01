from typing import Union

from src.schemas.categories import CategorySchemaAdd, CategoryPut, CategoryPatch
from src.utils.enum_classes import CategoryGroup
from src.utils.unit_of_work import IUnitOfWork
from src.utils.utils import get_start_month_date


class CategoriesService:
    async def add_one(
            self, uow: IUnitOfWork, user_id: int, category: CategorySchemaAdd
    ):
        category_dict = category.model_dump()
        async with uow:
            position = await uow.categories.define_position(user_id,
                                                            category.group)
            category_dict['position'] = position
            db_category = await uow.categories.add_one(user_id, category_dict)

            await uow.commit()
            return db_category

    async def remove_one(
            self, uow: IUnitOfWork, user_id: int, category_id: int
    ):
        async with uow:
            db_category = await uow.categories.drop_one(id=category_id)
            await uow.categories.update_positions(
                user_id=user_id, group=db_category.group, new_position=1000,
                old_position=db_category.position
            )
            await uow.commit()
            return db_category

    async def update_one(
            self, uow: IUnitOfWork, id: int, user_id: int,
            category: Union[CategoryPut, CategoryPatch]
    ):
        async with uow:
            db_category = await uow.categories.edit_one(user_id, id,
                                                        category.model_dump())
            await uow.commit()
            return db_category

    async def get_categories(
            self, uow: IUnitOfWork, user_id: int, group: CategoryGroup = None
    ):
        async with uow:
            categories = await uow.categories.find_all(
                user_id=user_id, group=group)

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

            return [x.to_read_model() for x in categories]
