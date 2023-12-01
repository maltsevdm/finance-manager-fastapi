import asyncio

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import update, select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from db import models
from db.database import async_session, engine
from db.models import Base, CategoryGroup, User
from db import schemas


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


async def update_category_amount(db: AsyncSession, user_id: int, category: schemas.CategoryUpdate):
    stmt = (update(models.Category)
            .values(amount=category.amount)
            .filter_by(user_id=user_id, name=category.name, group=category.group))
    await db.execute(stmt)
    await db.commit()


async def get_category_amount(db: AsyncSession, user_id: int, category: schemas.CategoryRead):
    query = (select(models.Category.amount)
             .filter_by(user_id=user_id, name=category.name, group=category.group))
    return (await db.execute(query)).scalars().first()


async def get_categories_by_group(db: AsyncSession, user_id: int, group: str):
    query = (select(models.Category).filter_by(user_id=user_id, group=group))
    result = (await db.execute(query)).scalars().all()
    return result


async def add_operation(db: AsyncSession, user_id: int, operation: schemas.OperationCreate):
    query = (select(models.Category.amount)
             .filter_by(user_id=user_id, name=operation.category_from, group=CategoryGroup.bank))
    result = (await db.execute(query)).scalars().first()
    if result is None:
        return 'error'
    stmt = (update(models.Category)
            .values(amount=result - operation.amount)
            .filter_by(user_id=user_id, name=operation.category_from, group=CategoryGroup.bank))
    await db.execute(stmt)

    query = (select(models.Category.amount)
             .filter_by(user_id=user_id, name=operation.category_to, group=CategoryGroup.expense))
    result = (await db.execute(query)).scalars().first()
    if result is None:
        return 'error'
    stmt = (update(models.Category)
            .values(amount=result + operation.amount)
            .filter_by(user_id=user_id, name=operation.category_to, group=CategoryGroup.expense))
    await db.execute(stmt)

    db_operation = models.Operation(user_id=user_id, **operation.__dict__)
    db.add(db_operation)

    new_balance = await calc_balance(db, user_id)
    await set_balance(db, user_id, new_balance)

    await db.commit()

    return db_operation


async def add_user_to_balance(db: AsyncSession, user_id: int):
    db_balance = models.Balance(user_id=user_id)
    db.add(db_balance)
    await db.commit()


async def calc_balance(db: AsyncSession, user_id: int):
    query = select(func.sum(models.Category.amount)).filter_by(user_id=user_id, group='bank')
    res = (await db.execute(query)).scalars().first()
    return res


async def set_balance(db: AsyncSession, user_id: int, new_balance):
    stmt = update(models.Balance).values(balance=new_balance).filter_by(user_id=user_id)
    await db.execute(stmt)
    await db.commit()


async def get_user_db():
    async with async_session() as db:
        yield SQLAlchemyUserDatabase(db, User)


if __name__ == '__main__':
    print(asyncio.run(calc_balance(1)))
