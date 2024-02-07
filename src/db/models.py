import datetime
from typing import Annotated

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, ForeignKey, TIMESTAMP, Index, text, \
    CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base
from src.utils.enum_classes import CategoryGroup, TransactionGroup, BankGroup

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
    __tablename__ = 'category'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))
    name: Mapped[str]
    group: Mapped[CategoryGroup]
    icon: Mapped[str | None]
    position: Mapped[int]
    bank_group: Mapped[BankGroup | None]
    amount: Mapped[float | None]
    card_balance: Mapped[float | None]
    credit_card_limit: Mapped[float | None]

    __table_args__ = (
        Index('user_group_name_index', 'user_id', 'name', 'group', unique=True),
        CheckConstraint('credit_card_limit >= 0', name='check_credit_card_limit'),
        CheckConstraint('position >= 0', name='check_position'),
        CheckConstraint('card_balance >= 0', name='check_card_balance'),
    )

    repr_cols_num = 7


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    group: Mapped[TransactionGroup]
    id_category_from: Mapped[int] = mapped_column(
        ForeignKey('category.id', ondelete='CASCADE'))
    id_category_to: Mapped[int] = mapped_column(
        ForeignKey('category.id', ondelete='CASCADE'))
    amount: Mapped[float]
    date: Mapped[datetime.date]
    note: Mapped[str | None]

    repr_cols_num = 8


class Debt(Base):
    __tablename__ = 'debts'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    bank_id: Mapped[int] = mapped_column(ForeignKey('category.id',
                                                    ondelete='CASCADE'))
    amount: Mapped[float]
    deadline: Mapped[datetime.date | None]
    notification: Mapped[bool]
    note: Mapped[str | None]

    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_amount'),
    )

