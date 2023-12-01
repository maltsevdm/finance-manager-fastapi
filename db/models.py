import datetime
import enum

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CategoryGroup(enum.Enum):
    income = "income"
    expense = "expense"
    bank = "bank"


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
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    group: Mapped[CategoryGroup] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False, default=0)

    # owner = relationship("User", back_populates="items")


class Balance(Base):
    __tablename__ = 'balance'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True, nullable=False)
    balance = Column(Integer, nullable=False, default=0)


class Operation(Base):
    __tablename__ = 'operation'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    category_from: Mapped[str] = mapped_column(nullable=False)
    category_to: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[datetime.date] = mapped_column(nullable=False)
