import datetime
from typing import Annotated

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base
from src.utils.enum_classes import (
    TransactionGroup, BankKindGroup, ExpenseIncomeGroup)

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


class CategoryId(Base):
    __tablename__ = 'categories_id'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))


class ExpenseIncomeCategory(Base):
    __tablename__ = 'expense_income_categories'

    id: Mapped[int] = mapped_column(
        ForeignKey('categories_id.id', ondelete='CASCADE'), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))
    name: Mapped[str]
    group: Mapped[ExpenseIncomeGroup]
    icon: Mapped[str | None]
    position: Mapped[int]
    monthly_limit: Mapped[float | None]

    __table_args__ = (
        Index('ei_cat_user_group_name_index', 'user_id', 'name', 'group',
              unique=True),
        CheckConstraint('monthly_limit >= 0', name='check_monthly_limit'),
    )

    repr_cols_num = 7


class Bank(Base):
    __tablename__ = 'banks'

    id: Mapped[int] = mapped_column(
        ForeignKey('categories_id.id', ondelete='CASCADE'), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))
    name: Mapped[str]
    group: Mapped[BankKindGroup]
    icon: Mapped[str | None]
    position: Mapped[int]
    amount: Mapped[float]
    credit_card_balance: Mapped[float | None]
    credit_card_limit: Mapped[float | None]

    __table_args__ = (
        Index('banks_user_group_name_index', 'user_id', 'name', 'group',
              unique=True),
        CheckConstraint('credit_card_limit >= 0',
                        name='check_credit_card_limit'),
        CheckConstraint('credit_card_balance >= 0',
                        name='check_credit_card_balance'),
    )

    repr_cols_num = 7

    def increase_amount(self, value: float) -> None:
        self.amount += value
        if self.group == BankKindGroup.credit_card:
            self.credit_card_balance += value

    def decrease_amount(self, value: float) -> None:
        self.amount -= value
        if self.group == BankKindGroup.credit_card:
            self.credit_card_balance -= value


class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    group: Mapped[TransactionGroup]
    bank_id: Mapped[int] = mapped_column(
        ForeignKey('banks.id', ondelete='CASCADE'))
    destination_id: Mapped[int] = mapped_column(
        ForeignKey('categories_id.id', ondelete='CASCADE'))
    amount: Mapped[float]
    date: Mapped[datetime.date]
    note: Mapped[str | None]

    repr_cols_num = 8


class Debt(Base):
    __tablename__ = 'debts'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    bank_id: Mapped[int] = mapped_column(ForeignKey('banks.id',
                                                    ondelete='CASCADE'))
    amount: Mapped[float]
    deadline: Mapped[datetime.date | None]
    notification: Mapped[bool]
    note: Mapped[str | None]

    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_amount'),
    )
