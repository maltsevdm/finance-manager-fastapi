from sqlalchemy import select, func

from src.db.models import Category
from src.utils.enum_classes import CategoryGroup
from src.utils.repository import SQLAlchemyRepository


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

    async def edit_one(self, data: dict, **filters):
        db_category = await self.find_one(**filters)

        for attr, value in data:
            if value is None:
                continue

            if attr == 'position':
                if db_category.position != value:
                    await self.update_positions(
                        db_category.user_id, db_category.group,
                        value, db_category.position)
                    db_category.position = value
                continue

            setattr(db_category, attr, value)

        return db_category

    async def calc_sum(self, **filters):
        query = select(func.sum(self.model.amount)).filter_by(**filters)
        res = await self.session.execute(query)
        return res.scalar_one()
