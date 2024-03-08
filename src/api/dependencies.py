import datetime
from typing import Annotated

from fastapi import Depends

from src.schemas.categories import BanksFilters
from src.schemas.transactions import TransactionsFilters
from src.utils.enum_classes import BankKindGroup, TransactionGroup, \
    TransactionStatus
from src.utils.unit_of_work import IUnitOfWork, UnitOfWork

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]


def get_banks_filters(
        id: int | None = None,
        group: BankKindGroup | None = None
):
    return BanksFilters(id=id, group=group)


def get_transactions_filters(
        id: int | None = None,
        group: TransactionGroup | None = None,
        bank_id: int | None = None,
        destination_id: int | None = None,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
        status: TransactionStatus | None = None
):
    return TransactionsFilters(
        id=id,
        group=group,
        bank_id=bank_id,
        destination_id=destination_id,
        date_from=date_from,
        date_to=date_to,
        status=status
    )
