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
    schemas.CategoryCreate(name='Продукты', group=CategoryGroup.expense,
                           icon='products.png'),
    schemas.CategoryCreate(name='Еда вне дома', group=CategoryGroup.expense,
                           icon='icons8-food-bar-100.png'),
    schemas.CategoryCreate(name='Транспорт', group=CategoryGroup.expense,
                           icon='transport.png'),
    schemas.CategoryCreate(name='Услуги', group=CategoryGroup.expense,
                           icon='icons8-scissors-100.png'),
    schemas.CategoryCreate(name='Прочее', group=CategoryGroup.expense,
                           icon='icons8-other-100.png'),
    schemas.CategoryCreate(name='Tinkoff Black', group=CategoryGroup.bank,
                           icon='money.png'),
]


async def create_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def add_category(
        user_id: int, category: schemas.CategoryCreate
):
    async with async_session() as db:
        query = (select(func.max(models.Category.position))
                 .filter_by(user_id=user_id, group=category.group))
        position = (await db.execute(query)).scalars().one()
        position = position + 1 if position else 1

        db_category = models.Category(
            user_id=user_id, name=category.name, group=category.group,
            icon=category.icon, position=position
        )
        db.add(db_category)
        await db.flush()

        db_category_amount = models.CategoryAmount(
            category_id=db_category.id, user_id=user_id,
            group=category.group
        )
        db.add(db_category_amount)

        await db.commit()
        return db_category


async def remove_category(user_id: int, category_id: int):
    async with async_session() as db:
        stmt = (delete(models.Category)
                .filter_by(id=category_id).returning(models.Category))
        db_category = (await db.execute(stmt)).scalars().one()
        await update_category_positions(
            db, user_id, db_category.group, 1000,
            db_category.position)
        await db.commit()
        return db_category


async def get_categories(user_id: int, group: CategoryGroup = None):
    async with async_session() as db:
        query = (select(models.Category).filter_by(user_id=user_id)
                 .order_by(models.Category.position))
        if group:
            query = query.filter_by(group=group)
        categories = (await db.execute(query)).scalars().all()

        query = (select(models.CategoryAmount.category_id,
                        models.CategoryAmount.amount)
                 .filter_by(user_id=user_id, date=utils.get_start_month_date()))
        if group:
            query = query.filter_by(group=group)
        category_amounts = (await db.execute(query)).all()

        category_amounts_dict = {}
        for category_amount in category_amounts:
            category_amounts_dict[category_amount[0]] = category_amount[1]

        for category in categories:
            category.amount = category_amounts_dict[category.id]

        return categories


async def update_category_positions(
        db: AsyncSession, user_id: int, group: CategoryGroup, new_position: int,
        old_position: int
):
    if old_position > new_position:
        query = (select(models.Category)
                 .filter(models.Category.user_id == user_id,
                         models.Category.group == group,
                         models.Category.position < old_position,
                         models.Category.position >= new_position))
        categories = (await db.execute(query)).scalars().all()
        for category in categories:
            category.position += 1
    else:
        query = (select(models.Category)
                 .filter(models.Category.user_id == user_id,
                         models.Category.group == group,
                         models.Category.position > old_position,
                         models.Category.position <= new_position))
        categories = (await db.execute(query)).scalars().all()
        for category in categories:
            category.position -= 1
    return categories


async def update_category(user_id: int, category: schemas.CategoryPut):
    async with async_session() as db:
        db_category = await db.get(models.Category, category.id)
        if db_category.position != category.position:
            await update_category_positions(
                db, user_id, db_category.group, category.position,
                db_category.position)

        stmt = (update(models.Category)
                .values(name=category.name, icon=category.icon,
                        position=category.position)
                .filter_by(id=category.id).returning(models.Category))
        db_category = (await db.execute(stmt)).scalars().one()

        stmt = (update(models.CategoryAmount)
                .values(amount=category.amount)
                .filter_by(id=category.id, date=utils.get_start_month_date()))
        await db.execute(stmt)

        await db.commit()
        return db_category


async def get_category_amount(
        db: AsyncSession, category_id: int,
        date: datetime.date = utils.get_start_month_date()
) -> models.CategoryAmount:
    query = (select(models.CategoryAmount)
             .filter_by(category_id=category_id, date=date))
    return (await db.execute(query)).scalars().one()


async def patch_category(user_id: int, category: schemas.CategoryPatch):
    async with async_session() as db:
        db_category = await db.get(models.Category, category.id)

        if category.name:
            db_category.name = category.name
        if category.position:
            await update_category_positions(
                db, user_id, db_category.group, category.position,
                db_category.position)
            db_category.position = category.position
        if category.icon:
            db_category.icon = category.icon

        db_category_amount = await get_category_amount(db, category.id)
        if category is not None:
            db_category_amount.amount = category.amount

        db_category.amount = db_category_amount.amount
        await db.commit()
        return db_category


async def get_transactions_by_group(
        db: AsyncSession, user_id: int, group: models.OperationGroup,
        date_from: datetime.date = utils.get_start_month_date(),
        date_to: datetime.date = None
):
    query = select(func.sum(models.Transaction.amount)).filter_by(
        user_id=user_id, group=group)
    query = query.filter(models.Transaction.date >= date_from)
    if date_to:
        query = query.filter(models.Transaction.date <= date_to)
    result = (await db.execute(query)).scalars().first()
    if result is None:
        return 0
    return result


async def add_transaction(user_id: int, transaction: schemas.TransactionCreate):
    async with async_session() as db:
        query = (select(models.CategoryAmount)
                 .filter_by(category_id=transaction.id_category_from,
                            date=utils.get_start_month_date()))
        db_category_from = (await db.execute(query)).scalar_one()
        db_category_from.amount -= transaction.amount

        query = (select(models.CategoryAmount)
                 .filter_by(category_id=transaction.id_category_to,
                            date=utils.get_start_month_date()))
        db_category_to = (await db.execute(query)).scalar_one()
        db_category_to.amount += transaction.amount

        db_operation = models.Transaction(
            user_id=user_id, group=transaction.group,
            category_from=transaction.id_category_from,
            category_to=transaction.id_category_to,
            amount=transaction.amount, date=transaction.date,
            note=transaction.note
        )
        db.add(db_operation)

        new_balance = await get_balance(db, user_id)
        await set_balance(db, user_id, new_balance)

        await db.commit()

        expenses = await get_transactions_by_group(
            db, user_id, models.OperationGroup.expense)
        incomes = await get_transactions_by_group(
            db, user_id, models.OperationGroup.income)

        return {
            'new_balance': new_balance,
            'amount_category_from': db_category_from.amount,
            'amount_category_to': db_category_to.amount,
            'expenses': expenses,
            'incomes': incomes
        }


async def add_user_to_balance(user_id: int):
    async with async_session() as db:
        db_balance = models.Balance(user_id=user_id)
        db.add(db_balance)
        await db.commit()


async def get_balance(
        db: AsyncSession, user_id: int,
        date: datetime.date = utils.get_start_month_date()
):
    query = (select(func.sum(models.CategoryAmount.amount))
             .filter_by(user_id=user_id, group=CategoryGroup.bank.value,
                        date=date))
    return (await db.execute(query)).scalars().first()


async def get_last_date(db: AsyncSession, user_id: int):
    query = (select(models.CategoryAmount.date)
             .filter_by(user_id=user_id)
             .order_by(models.CategoryAmount.date.desc()))
    return (await db.execute(query)).scalars().first()


async def set_balance(db: AsyncSession, user_id: int, new_balance):
    stmt = (update(models.Balance).values(balance=new_balance)
            .filter_by(user_id=user_id, date=utils.get_start_month_date()))
    await db.execute(stmt)
    await db.commit()


async def get_user_db():
    async with async_session() as db:
        yield SQLAlchemyUserDatabase(db, User)


async def get_user_categories(db: AsyncSession, user_id: int, date):
    query = (select(
        models.Category.name, models.Category.group, models.Category.icon,
        models.Category.amount, models.Category.position)
             .filter_by(user_id=user_id, date=date))
    return (await db.execute(query)).all()


async def prepare_db_for_user(db: AsyncSession, user_id: int):
    last_date = await get_last_date(db, user_id)
    if last_date is None:
        for category in categories_start_pack:
            await add_category(db, user_id, category)
    else:
        user_categories = await get_user_categories(db, user_id, last_date)
        for name, group, icon, amount, position in user_categories:
            await add_category(
                db, user_id,
                schemas.CategoryCreate(
                    name=name, group=group, icon=icon,
                    amount=amount if group == CategoryGroup.bank else 0,
                    position=position

                )
            )


async def test():
    async with async_session() as db:
        print(await get_category_amount(db, 1))


if __name__ == '__main__':
    asyncio.run(test())
