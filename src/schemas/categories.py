from pydantic import BaseModel

from src.utils.enum_classes import CategoryGroup


class CategoryAdd(BaseModel):
    name: str
    group: CategoryGroup
    icon: str | None = None
    credit_card_limit: float | None = None
    card_balance: float | None = None
    amount: float | None = None


class CategoryRead(CategoryAdd):
    id: int
    user_id: int
    position: int


class CategoryUpdate(BaseModel):
    name: str | None = None
    amount: float | int | None = None
    position: int | None = None
    icon: str | None = None
    credit_card_limit: float | None = None
    bank_balance: float | None = None
