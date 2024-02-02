from src.schemas.categories import CategoryAdd, CategoryUpdate, CategoryRead
from src.utils.enum_classes import CategoryGroup
from src.utils.unit_of_work import IUnitOfWork
from src.utils.utils import get_start_month_date


class CategoriesService:
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

            return [CategoryRead.model_validate(x, from_attributes=True)
                    for x in categories]

    async def add_one(
            self, uow: IUnitOfWork, user_id: int, category: CategoryAdd
    ):
        category_dict = category.model_dump()
        async with uow:
            position = await uow.categories.define_position(user_id,
                                                            category.group)
            category_dict['position'] = position
            category_dict['user_id'] = user_id
            db_category = await uow.categories.add_one(category_dict)

            await uow.commit()
            return db_category

    async def update_one(
            self, uow: IUnitOfWork, id: int, user_id: int,
            category: CategoryUpdate
    ):
        async with uow:
            db_category = await uow.categories.edit_one(
                id=id, user_id=user_id, data=category.model_dump())
            await uow.commit()
            return db_category

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
            return db_category
