import datetime

from pydantic import BaseModel

from db.models import CategoryGroup, OperationGroup


class CategoryBase(BaseModel):
    name: str
    group: CategoryGroup


class CategoryCreate(CategoryBase):
    icon: str
    position: int


class CategoryRead(BaseModel):
    id: int
    user_id: int
    name: str
    group: CategoryGroup
    icon: str
    position: int


class CategoryUpdate(BaseModel):
    id: int
    name: str
    amount: int
    position: int
    icon: str


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
    id_category_from: int
    id_category_to: int
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
