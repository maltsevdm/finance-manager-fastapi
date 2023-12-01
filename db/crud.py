from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

import db.models as models
import db.schemas as schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def get_categories(db: AsyncSession):
    query = select(models.Category)
    result = (await db.execute(query)).all()
    return result


def get_category_by_title(db: Session, title: str):
    return db.query(models.Category).filter(models.Category.title == title).first()


def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def create_expense(db: Session, expense: schemas.ExpenditureCreate):
    db_expense = models.Expenditure(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def set_balance(db: Session, balance: schemas.BalanceCreate):
    db_balance = models.Balance(**balance.model_dump())
    db.add(db_balance)
    db.commit()
    db.refresh(db_balance)
    return db_balance


def get_balance_by_user_id(db: Session, user_id: int):
    return db.query(models.Balance).filter(models.Balance.id_user == user_id).first()


def update_balance(db: Session, balance: schemas.BalanceCreate):
    pass
