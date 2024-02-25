from sqlalchemy import select, func, insert, delete

from src.db.models import CategoryId
from src.utils.repository import SQLAlchemyRepository


class CategoriesRepository(SQLAlchemyRepository):
    position_criteria: list

    async def add_one(self, data: dict):
        stmt = (insert(CategoryId).values(user_id=data['user_id'])
                .returning(CategoryId.id))
        res = await self.session.execute(stmt)
        data['id'] = res.scalar_one()

        position_filter = {c: data[c] for c in self.position_criteria}
        data['position'] = await self._define_position(**position_filter)
        return await super().add_one(data)

    async def _define_position(self, **filters):
        query = select(func.max(self.model.position)).filter_by(**filters)
        position: int = (await self.session.execute(query)).scalars().one()
        return position + 1 if position else 1

    async def _update_positions(
            self, new_position: int, old_position: int, **filters
    ):
        if old_position > new_position:
            query = (select(self.model)
                     .filter(self.model.position < old_position,
                             self.model.position >= new_position))
            query = query.filter_by(**filters)
            categories = (await self.session.execute(query)).scalars().all()
            for category in categories:
                category.position += 1
        else:
            query = (select(self.model)
                     .filter(self.model.position > old_position,
                             self.model.position <= new_position))
            query = query.filter_by(**filters)
            categories = (await self.session.execute(query)).scalars().all()
            for category in categories:
                category.position -= 1
        return categories

    async def edit_one(self, data: dict, **filters):
        db_category = await self.find_one(**filters)

        for attr, value in data.items():
            if value is None:
                continue

            if attr == 'position':
                if db_category.position != value:
                    position_filter = {c: getattr(db_category, c)
                                       for c in self.position_criteria}
                    await self._update_positions(
                        db_category.user_id, db_category.group,
                        **position_filter)
                    db_category.position = value
                continue

            setattr(db_category, attr, value)

        return db_category

    async def drop_one(self, **filters):
        db_category = await super().drop_one(**filters)

        stmt = delete(CategoryId).filter_by(id=db_category.id)
        await self.session.execute(stmt)

        position_filter = {c: getattr(db_category, c)
                           for c in self.position_criteria}
        await self._update_positions(
            new_position=1000, old_position=db_category.position,
            **position_filter
        )
        return db_category

    async def calc_sum(self, **filters):
        query = select(func.sum(self.model.amount)).filter_by(**filters)
        res = await self.session.execute(query)
        return res.scalar_one()
