import datetime

from pydantic import BaseModel

from src.utils.enum_classes import OperationGroup


class TransactionCreate(BaseModel):
    group: OperationGroup
    id_category_from: int
    id_category_to: int
    amount: int
    date: datetime.date = datetime.date.today()
    note: str = ''


class OperationBase(BaseModel):
    type: str
    category: str
    amount: int
