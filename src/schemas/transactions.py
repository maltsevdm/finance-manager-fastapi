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
    note: str | None = None


class TransactionRead(TransactionAdd):
    id: int
    user_id: int


class TransactionPrettyRead(BaseModel):
    id: int
    group: TransactionGroup
    bank_name: str
    destination_name: str
    amount: float
    date: datetime.date
    note: str | None


class TransactionUpdate(BaseModel):
    bank_id: Optional[int] = None
    destination_id: Optional[int] = None
    amount: Optional[float] = None
    date: Optional[datetime.date] = None
    note: Optional[str] = None


class TransactionsFilters(BaseModel):
    id: int | None = None
    group: TransactionGroup | None = None
    bank_id: int | None = None
    destination_id: int | None = None
    date_from: datetime.date | None = None
    date_to: datetime.date | None = None