import datetime

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
