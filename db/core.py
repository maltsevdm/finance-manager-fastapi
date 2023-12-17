import asyncio
import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import update, select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

import utils
from db import models
from db.database import async_session, engine, get_async_session
from db.models import Base, CategoryGroup, User
from db import schemas

categories_start_pack = [
    schemas.CategoryCreate(name='Продукты', group=CategoryGroup.expense, icon='products.png', position=1),
    schemas.CategoryCreate(name='Еда вне дома', group=CategoryGroup.expense, icon='icons8-food-bar-100.png', position=2),
    schemas.CategoryCreate(name='Транспорт', group=CategoryGroup.expense, icon='transport.png', position=3),
    schemas.CategoryCreate(name='Услуги', group=CategoryGroup.expense, icon='icons8-scissors-100.png', position=4),
    schemas.CategoryCreate(name='Прочее', group=CategoryGroup.expense, icon='icons8-other-100.png', position=5),
    schemas.CategoryCreate(name='Tinkoff Black', group=CategoryGroup.bank, icon='money.png', position=1),
]


async def create_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def add_category(db: AsyncSession, user_id: int, category: schemas.CategoryCreate):
    db_category = models.Category(user_id=user_id, **category.__dict__)
    db.add(db_category)
    await db.commit()
    return db_category


async def remove_category(db: AsyncSession, user_id: int, category: schemas.CategoryRemove):
    stmt = (delete(models.Category)
            .filter_by(user_id=user_id, name=category.name, group=category.group))
    await db.execute(stmt)
    await db.commit()


async def get_category_amount(db: AsyncSession, user_id: int, category: schemas.CategoryRead):
    query = (select(models.Category.amount)
             .filter_by(user_id=user_id, name=category.name, group=category.group))
    return (await db.execute(query)).scalars().first()


async def get_categories_by_group(
        db: AsyncSession, user_id: int, group: CategoryGroup, date=utils.get_start_month_date()
):
    query = (select(models.Category.name, models.Category.icon, models.Category.amount)
             .filter_by(user_id=user_id, group=group, date=date).order_by(models.Category.position))
    result = (await db.execute(query)).all()
    return result


async def update_category_amount(db: AsyncSession, user_id: int, category: schemas.CategoryUpdate):
    stmt = (update(models.Category)
            .values(amount=category.amount)
            .filter_by(user_id=user_id, name=category.name, group=category.group))
    await db.execute(stmt)


async def get_transactions_by_group(
        db: AsyncSession, user_id: int, group: models.OperationGroup,
        date_from: datetime.date = utils.get_start_month_date(), date_to: datetime.date = None):
    query = select(func.sum(models.Transaction.amount)).filter_by(user_id=user_id, group=group)
    query = query.filter(models.Transaction.date >= date_from)
    if date_to:
        query = query.filter(models.Transaction.date <= date_to)
    result = (await db.execute(query)).scalars().first()
    if result is None:
        return 0
    return result


async def add_operation(db: AsyncSession, user_id: int, operation: schemas.TransactionCreate):
    query = (select(models.Category.amount)
             .filter_by(user_id=user_id, name=operation.category_from, group=CategoryGroup.bank))
    amount_cat_from = (await db.execute(query)).scalars().first()
    if amount_cat_from is None:
        return 'error'
    amount_cat_from -= operation.amount
    await update_category_amount(db, user_id,
                                 schemas.CategoryUpdate(name=operation.category_from, group=CategoryGroup.bank,
                                                        amount=amount_cat_from))

    query = (select(models.Category.amount)
             .filter_by(user_id=user_id, name=operation.category_to, group=CategoryGroup.expense))
    amount_cat_to = (await db.execute(query)).scalars().first()
    if amount_cat_to is None:
        return 'error'

    amount_cat_to += operation.amount
    await update_category_amount(db, user_id,
                                 schemas.CategoryUpdate(name=operation.category_to, group=CategoryGroup.expense,
                                                        amount=amount_cat_to))

    db_operation = models.Transaction(user_id=user_id, **operation.__dict__)
    db.add(db_operation)

    new_balance = await get_balance(db, user_id)
    await set_balance(db, user_id, new_balance)

    await db.commit()

    expenses = await get_transactions_by_group(db, user_id, models.OperationGroup.expense)
    incomes = await get_transactions_by_group(db, user_id, models.OperationGroup.income)

    return {
        'new_balance': new_balance,
        'amount_category_from': amount_cat_from,
        'amount_category_to': amount_cat_to,
        'expenses': expenses,
        'incomes': incomes
    }


async def add_user_to_balance(user_id: int):
    async with async_session() as db:
        db_balance = models.Balance(user_id=user_id)
        db.add(db_balance)
        await db.commit()


async def get_balance(db: AsyncSession, user_id: int, date: datetime.date = utils.get_start_month_date()):
    query = select(func.sum(models.Category.amount)).filter_by(user_id=user_id, group='bank', date=date)
    return (await db.execute(query)).scalars().first()


async def get_last_date(db: AsyncSession, user_id: int):
    query = select(models.Category.date).filter_by(user_id=user_id).order_by(models.Category.date.desc())
    return (await db.execute(query)).scalars().first()


async def set_balance(db: AsyncSession, user_id: int, new_balance):
    stmt = update(models.Balance).values(balance=new_balance).filter_by(user_id=user_id)
    await db.execute(stmt)
    await db.commit()


async def get_user_db():
    async with async_session() as db:
        yield SQLAlchemyUserDatabase(db, User)


async def get_user_categories(db: AsyncSession, user_id: int, date):
    query = (select(
        models.Category.name, models.Category.group, models.Category.icon, models.Category.amount)
             .filter_by(user_id=user_id, date=date))
    return (await db.execute(query)).all()


async def prepare_db_for_user(db: AsyncSession, user_id: int):
    last_date = await get_last_date(db, user_id)
    if last_date is None:
        for category in categories_start_pack:
            await add_category(db, user_id, category)
    else:
        user_categories = await get_user_categories(db, user_id, last_date)
        for name, group, icon, amount in user_categories:
            await add_category(
                db, user_id,
                schemas.CategoryCreate(
                    name=name, group=group, icon=icon, amount=amount if group == CategoryGroup.bank else 0
                )
            )


async def test():
    async with async_session() as db:
        print('======> ', await prepare_db_for_user(db, 1))


if __name__ == '__main__':
    asyncio.run(test())
