import datetime
from typing import Optional

from sqlalchemy import select, func, update

from src.db.models import Category, CategoryAmount
from src.utils import utils
from src.utils.enum_classes import CategoryGroup
from src.utils.repository import SQLAlchemyRepository
from src.schemas.categories import CategoryPut


class CategoriesRepository(SQLAlchemyRepository):
    model = Category

    async def define_position(self, user_id: int, group: CategoryGroup):
        query = (select(func.max(self.model.position))
                 .filter_by(user_id=user_id, group=group))
        position = (await self.session.execute(query)).scalars().one()
        return position + 1 if position else 1

    async def update_positions(
            self, user_id: int, group: CategoryGroup,
            new_position: int, old_position: int
    ):
        if old_position > new_position:
            query = (select(self.model)
                     .filter(self.model.user_id == user_id,
                             self.model.group == group,
                             self.model.position < old_position,
                             self.model.position >= new_position))
            categories = (await self.session.execute(query)).scalars().all()
            for category in categories:
                category.position += 1
        else:
            query = (select(self.model)
                     .filter(self.model.user_id == user_id,
                             self.model.group == group,
                             self.model.position > old_position,
                             self.model.position <= new_position))
            categories = (await self.session.execute(query)).scalars().all()
            for category in categories:
                category.position -= 1
        return categories

    async def find_all(
            self,
            user_id: int,
            date: datetime.date = utils.get_start_month_date(),
            group: Optional[CategoryGroup] = None
    ):
        query = select(self.model).filter(self.model.user_id == user_id)

        if group:
            query = query.filter_by(group=group)

        res = await self.session.execute(query)
        return res.scalars().all()

    async def edit_one(self, user_id: int, id: int, data: dict):
        db_category = await self.session.get(self.model, id)

        if data['name'] is not None:
            db_category.name = data['name']
        if data['icon'] is not None:
            db_category.icon = data['icon']
        if data['amount'] is not None:
            db_category.amount = data['amount']
        if data['position'] is not None:
            if db_category.position != data['position']:
                await self.update_positions(
                    user_id, db_category.group, data['position'],
                    db_category.position)
            db_category.position = data['position']

        return db_category

    async def calc_sum(self, **filters):
        query = select(func.sum(self.model.amount)).filter_by(**filters)
        res = await self.session.execute(query)
        return res.scalar_one()
