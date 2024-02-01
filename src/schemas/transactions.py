import datetime
from typing import Optional

from pydantic import BaseModel

from src.utils.enum_classes import TransactionGroup


class TransactionSchema(BaseModel):
    id: int
    user_id: int
    group: TransactionGroup
    id_category_from: int
    id_category_to: int
    amount: float
    date: datetime.date
    note: str


class TransactionCreate(BaseModel):
    id_category_from: int
    id_category_to: int
    amount: float
    date: datetime.date = datetime.date.today()
    note: str = ''


class TransactionUpdate(BaseModel):
    id_category_from: Optional[int] = None
    id_category_to: Optional[int] = None
    amount: Optional[float] = None
    date: Optional[datetime.date] = None
    note: Optional[str] = None
