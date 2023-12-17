import datetime

from pydantic import BaseModel

from db.models import CategoryGroup, OperationGroup


class CategoryBase(BaseModel):
    name: str
    group: CategoryGroup


class CategoryCreate(CategoryBase):
    icon: str
    amount: int = 0
    position: int


class CategoryRemove(CategoryBase):
    pass


class CategoryRead(BaseModel):
    name: str
    icon: str
    amount: int


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


class TransactionCreate(BaseModel):
    group: OperationGroup
    category_from: str
    category_to: str
    amount: int
    date: datetime.date = datetime.date.today()


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
