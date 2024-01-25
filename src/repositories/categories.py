import datetime
from typing import Optional

from sqlalchemy import select, func

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
        query = (select(
            self.model.id,
            self.model.name,
            self.model.group,
            self.model.icon,
            self.model.position,
            CategoryAmount.amount
        ).join(CategoryAmount, self.model.id == CategoryAmount.category_id)
         .filter(
            CategoryAmount.date == date,
            self.model.user_id == user_id
        ))

        if group:
            query = query.filter(self.model.group == group)

        res = await self.session.execute(query)
        return res.all()

    async def edit_one(self, user_id: int, category: CategoryPut):
        db_category = await self.session.get(self.model, category.id)
        if db_category.position != category.position:
            await self.update_positions(
                user_id, db_category.group, category.position,
                db_category.position)

        db_category.name = category.name
        db_category.icon = category.icon
        db_category.position = category.position

        return db_category

        stmt = (update(models.CategoryAmount)
                .values(amount=category.amount)
                .filter_by(id=category.id, date=utils.get_start_month_date()))
        await db.execute(stmt)

        await db.commit()
        return db_category
