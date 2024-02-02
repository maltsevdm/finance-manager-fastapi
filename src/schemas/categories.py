import datetime
from typing import Optional, Union

from pydantic import BaseModel

from src.utils.enum_classes import CategoryGroup


class CategoryAdd(BaseModel):
    name: str
    group: CategoryGroup
    icon: str | None = None


class CategoryRead(CategoryAdd):
    id: int
    user_id: int
    position: int
    amount: float


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    amount: Union[float, int, None] = None
    position: Optional[int] = None
    icon: Optional[str] = None
