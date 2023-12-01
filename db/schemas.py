import datetime

from pydantic import BaseModel

from db.models import CategoryGroup, OperationGroup


class CategoryBase(BaseModel):
    name: str
    group: CategoryGroup


class CategoryCreate(CategoryBase):
    icon: str


class CategoryRemove(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    amount: int


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class OperationCreate(BaseModel):
    group: OperationGroup
    category_from: str
    category_to: str
    amount: int
    date: datetime.date


class OperationBase(BaseModel):
    type: str
    category: str
    amount: int


class ExpenditureBase(BaseModel):
    id_user: int
    amount: int
    category: str


class ExpenditureCreate(ExpenditureBase):
    pass


class Expenditure(ExpenditureBase):
    id: int
    date: datetime.datetime

    class Config:
        orm_mode = True


class BalanceBase(BaseModel):
    id_user: int
    balance: int = 0


class BalanceCreate(BalanceBase):
    pass


class Balance(BalanceBase):
    pass

    class Config:
        orm_mode = True
