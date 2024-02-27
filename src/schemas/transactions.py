import datetime
from typing import Optional

from pydantic import BaseModel

from src.utils.enum_classes import TransactionGroup


class TransactionAdd(BaseModel):
    group: TransactionGroup
    bank_id: int
    destination_id: int
    amount: float
    date: datetime.date = datetime.date.today()
    note: str | None


class TransactionRead(TransactionAdd):
    id: int
    user_id: int


class TransactionUpdate(BaseModel):
    bank_id: Optional[int] = None
    destination_id: Optional[int] = None
    amount: Optional[float] = None
    date: Optional[datetime.date] = None
    note: Optional[str] = None
