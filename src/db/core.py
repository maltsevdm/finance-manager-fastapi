from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.categories import ExpenseIncomeAdd
import src.schemas.transactions
import src.utils.enum_classes
from src.db import models
from src.db.database import async_session, engine, Base
from src.db.models import User
from src.utils.enum_classes import CategoryGroup


# categories_start_pack = [
#     CategoryAdd(name='Продукты', group=CategoryGroup.expense,
#                 icon='products.png'),
#     CategoryAdd(name='Еда вне дома', group=CategoryGroup.expense,
#                 icon='icons8-food-bar-100.png'),
#     CategoryAdd(name='Транспорт', group=CategoryGroup.expense,
#                 icon='transport.png'),
#     CategoryAdd(name='Услуги', group=CategoryGroup.expense,
#                 icon='icons8-scissors-100.png'),
#     CategoryAdd(name='Прочее', group=CategoryGroup.expense,
#                 icon='icons8-other-100.png'),
#     CategoryAdd(name='Tinkoff Black', group=CategoryGroup.bank,
#                 icon='money.png'),
# ]


async def create_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_user_db():
    async with async_session() as db:
        yield SQLAlchemyUserDatabase(db, User)


async def get_user_categories(db: AsyncSession, user_id: int, date):
    query = (select(
        models.Category.name, models.Category.group, models.Category.icon,
        models.Category.position)
             .filter_by(user_id=user_id, date=date))
    return (await db.execute(query)).all()


async def prepare_db_for_user(user_id: int):
    async with async_session() as db:
        last_date = await get_last_date(db, user_id)
        if last_date is None:
            for category in categories_start_pack:
                await add_category(db, user_id, category)
        else:
            user_categories = await get_user_categories(db, user_id, last_date)
            for name, group, icon, amount, position in user_categories:
                await add_category(
                    db, user_id,
                    src.schemas.categories.ExpenseIncomeAdd(
                        name=name, group=group, icon=icon,
                        amount=amount if group == CategoryGroup.bank else 0,
                        position=position

                    )
                )
