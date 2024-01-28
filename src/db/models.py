import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base
from src.schemas.categories import CategorySchema, CategoryAmountSchema
from src.schemas.transactions import TransactionSchema
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
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    group: Mapped[CategoryGroup] = mapped_column(nullable=False)
    icon: Mapped[str] = mapped_column(nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(default=0)

    def to_read_model(self) -> CategorySchema:
        return CategorySchema(
            id=self.id,
            user_id=self.user_id,
            name=self.name,
            group=self.group,
            icon=self.icon,
            position=self.position,
            amount=self.amount
        )


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

    def to_read_model(self) -> CategoryAmountSchema:
        return CategoryAmountSchema(
            id=self.id,
            category_id=self.category_id,
            user_id=self.user_id,
            group=self.group,
            date=self.date,
            amount=self.amount
        )


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
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    group: Mapped[TransactionGroup] = mapped_column(nullable=False)
    id_category_from: Mapped[int] = mapped_column(
        ForeignKey('category.id', ondelete='CASCADE'),
        nullable=False)
    id_category_to: Mapped[int] = mapped_column(
        ForeignKey('category.id', ondelete='CASCADE'),
        nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    date: Mapped[datetime.date] = mapped_column(nullable=False)
    note: Mapped[str]

    def to_read_model(self) -> TransactionSchema:
        return TransactionSchema(
            id=self.id,
            user_id=self.user_id,
            group=self.group,
            id_category_from=self.id_category_from,
            id_category_to=self.id_category_to,
            amount=self.amount,
            date=self.date,
            note=self.note,
        )
