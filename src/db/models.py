import datetime
from typing import Optional

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String, TIMESTAMP,
                        Index, Float, text)
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base
from src.utils import utils
from src.utils.enum_classes import CategoryGroup, TransactionGroup


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))
    name: Mapped[str]
    group: Mapped[CategoryGroup]
    icon: Mapped[str | None]
    position: Mapped[int]
    amount: Mapped[float] = mapped_column(server_default=text('0'))

    __table_args__ = (
        Index('user_group_name_index', 'user_id', 'name', 'group', unique=True),
    )

    repr_cols_num = 7


class CategoryAmount(Base):
    __tablename__ = 'category_amount'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey('category.id', ondelete='CASCADE'),
        nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False)
    group: Mapped[CategoryGroup] = mapped_column(nullable=False)
    date: Mapped[datetime.date] = mapped_column(
        nullable=False, default=utils.get_start_month_date())
    amount: Mapped[float] = mapped_column(nullable=False, default=0)

    repr_cols_num = 6


class Balance(Base):
    __tablename__ = 'balance'

    user_id = Column(
        Integer, ForeignKey('user.id'), primary_key=True, nullable=False)
    balance = Column(Integer, nullable=False, default=0)
    date: Mapped[datetime.date] = mapped_column(
        nullable=False, default=utils.get_start_month_date())


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
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
