import datetime
from typing import Optional, Union

from pydantic import BaseModel

from src.utils.enum_classes import CategoryGroup


class CategorySchema(BaseModel):
    id: int
    user_id: int
    name: str
    group: CategoryGroup
    icon: str
    position: int
    amount: float


class CategoryAmountSchema(BaseModel):
    id: int
    category_id: int
    user_id: int
    group: CategoryGroup
    date: datetime.date
    amount: float


class CategoryBase(BaseModel):
    name: str
    group: CategoryGroup


class CategorySchemaAdd(CategoryBase):
    icon: str


class CategoryRead(BaseModel):
    id: int
    user_id: int
    name: str
    group: CategoryGroup
    icon: str
    position: int
    amount: float


class CategoryPut(BaseModel):
    name: str
    amount: Union[float, int]
    position: int
    icon: str


class CategoryPatch(BaseModel):
    name: Optional[str] = None
    amount: Union[float, int, None] = None
    position: Optional[int] = None
    icon: Optional[str] = None
