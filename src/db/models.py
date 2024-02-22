import datetime
from typing import Annotated

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base
from src.utils.enum_classes import CategoryGroup, TransactionGroup, \
    BankKindGroup

intpk = Annotated[int, mapped_column(primary_key=True)]


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[intpk]
    email: Mapped[str]
    username: Mapped[str]
    registered_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))
    name: Mapped[str]
    group: Mapped[CategoryGroup]  # bank | expense | income
    icon: Mapped[str | None]
    position: Mapped[int]

    __table_args__ = (
        Index('user_group_name_index', 'user_id', 'name', 'group', unique=True),
        CheckConstraint('position >= 0', name='categories_check_position'),
    )

    repr_cols_num = 7


class ExpenseIncomeCategory(Base):
    __tablename__ = 'expense_income_categories'

    id: Mapped[int] = mapped_column(
        ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
    monthly_limit: Mapped[float | None]

    __table_args__ = (
        CheckConstraint('monthly_limit >= 0', name='check_monthly_limit'),
    )

    repr_cols_num = 2


class Bank(Base):
    __tablename__ = 'banks'

    id: Mapped[int] = mapped_column(
        ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
    bank_group: Mapped[BankKindGroup]
    amount: Mapped[float]
    credit_card_balance: Mapped[float | None]
    credit_card_limit: Mapped[float | None]

    __table_args__ = (
        CheckConstraint('credit_card_limit >= 0',
                        name='check_credit_card_limit'),
        CheckConstraint('credit_card_balance >= 0',
                        name='check_credit_card_balance'),
    )

    repr_cols_num = 5


class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    group: Mapped[TransactionGroup]
    id_category_from: Mapped[int] = mapped_column(
        ForeignKey('categories.id', ondelete='CASCADE'))
    id_category_to: Mapped[int] = mapped_column(
        ForeignKey('categories.id', ondelete='CASCADE'))
    amount: Mapped[float]
    date: Mapped[datetime.date]
    note: Mapped[str | None]

    repr_cols_num = 8


class Debt(Base):
    __tablename__ = 'debts'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    bank_id: Mapped[int] = mapped_column(ForeignKey('categories.id',
                                                    ondelete='CASCADE'))
    amount: Mapped[float]
    deadline: Mapped[datetime.date | None]
    notification: Mapped[bool]
    note: Mapped[str | None]

    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_amount'),
    )
