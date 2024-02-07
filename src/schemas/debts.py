import datetime

from pydantic import BaseModel


class DebtAdd(BaseModel):
    bank_id: int
    amount: float
    deadline: datetime.date | None = None
    notification: bool
    note: str | None = None


class DebtRead(DebtAdd):
    id: int
    user_id: int


class DebtUpdate(BaseModel):
    bank_id: int | None = None
    amount: float | None = None
    deadline: datetime.date | None = None
    notification: bool | None = None
    note: str | None = None
