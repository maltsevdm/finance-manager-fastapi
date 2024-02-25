from abc import ABC
from typing import Type

from pydantic import BaseModel

from src.db.database import async_session
from src.repositories.categories import CategoriesRepository
from src.utils.unit_of_work import IUnitOfWork


class CategoriesService(ABC):
    repository: Type[CategoriesRepository]
    schema_read: BaseModel

    async def get_all(self, uow: IUnitOfWork, **filters):
        async with async_session() as session:
            categories = await self.repository(session).find_all(**filters)

            return [
                self.schema_read.model_validate(category, from_attributes=True)
                for category in categories]

    async def add_one(
            self, uow: IUnitOfWork, user_id: int,
            category: BaseModel
    ):
        async with async_session() as session:
            category_dict = category.model_dump()
            category_dict['user_id'] = user_id

            db_category = await self.repository(session).add_one(category_dict)
            await session.commit()

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
            return self.schema_read.model_validate(db_category,
                                                   from_attributes=True)

    async def remove_one(
            self, uow: IUnitOfWork, user_id: int, category_id: int
    ):
        async with async_session() as session:
            db_category = await self.repository(session).drop_one(
                id=category_id, user_id=user_id)
            await session.commit()
            return self.schema_read.model_validate(db_category,
                                                   from_attributes=True)
