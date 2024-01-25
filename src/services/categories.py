from sqlalchemy import select

from src.db.models import Category, CategoryAmount
from src.schemas.categories import CategorySchemaAdd, CategoryPut
from src.utils import utils
from src.utils.enum_classes import CategoryGroup
from src.utils.unit_of_work import IUnitOfWork


class CategoriesService:
    async def add_category(
            self, uow: IUnitOfWork, user_id: int, category: CategorySchemaAdd
    ):
        category_dict = category.model_dump()
        async with uow:
            position = await uow.categories.define_position(user_id,
                                                            category.group)
            category_dict['position'] = position
            db_category = await uow.categories.add_one(user_id, category_dict)

            category_amount_dict = {
                'category_id': db_category.id,
                'group': category.group
            }
            await uow.categories_amount.add_one(user_id, category_amount_dict)

            await uow.commit()
            return db_category

    async def remove_category(
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

    async def update_category(
            self, uow: IUnitOfWork, user_id: int, category: CategoryPut
    ):
        async with uow:
            db_category = await uow.categories.edit_one(user_id, category)
            await uow.categories_amount.edit_one(
                db_category.id, amount=category.amount,
                date=utils.get_start_month_date()
            )
            await uow.commit()
            return db_category


    async def get_categories(
            self, uow: IUnitOfWork, user_id: int, group: CategoryGroup = None
    ):
        async with uow:
            return await uow.categories.find_all(user_id=user_id, group=group)



