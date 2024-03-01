import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound

from src.api.dependencies import UOWDep, get_transactions_filters
from src.auth.manager import current_active_user
from src.db.models import User
from src.schemas.transactions import (
    TransactionAdd, TransactionUpdate, TransactionRead, TransactionsFilters)
from src.services.transactions import TransactionsService
from src.utils import utils
from src.utils.enum_classes import TransactionGroup

router = APIRouter(prefix='/transactions', tags=['Transaction'])


@router.post('/', response_model=TransactionRead)
async def add_transaction(
        uow: UOWDep,
        transaction: TransactionAdd,
        user: User = Depends(current_active_user),
):
    try:
        res = await TransactionsService().add_one(uow, user.id, transaction)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail='Одна из категорий не существует')
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=ex.args[0])
    return res


@router.delete('/{id}', response_model=TransactionRead)
async def remove_transaction(
        uow: UOWDep,
        id: int,
        user: User = Depends(current_active_user),
):
    try:
        res = await TransactionsService().remove_one(uow, id, user.id)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail=f'Нет транзакции с {id=}')
    return res


@router.patch('/{id}')
async def update_transaction(
        uow: UOWDep,
        id: int,
        transaction: TransactionUpdate,
        user: User = Depends(current_active_user),
):
    try:
        res = await TransactionsService().update_one(
            uow, id, transaction, user.id)
    except ValueError:
        raise HTTPException(status_code=400,
                            detail='Неверное направление транзакции')
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail=f'Нет транзакции с {id=}')
    return res


@router.get('/')
async def get_transactions(
        uow: UOWDep,
        offset: int = 0,
        limit: int = 100,
        id: int | None = None,
        group: TransactionGroup | None = None,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
        user: User = Depends(current_active_user),
):
    if offset < 0:
        raise HTTPException(
            status_code=422,
            detail='OFFSET не может быть отрицательным'
        )
    if limit < 0:
        raise HTTPException(
            status_code=422,
            detail='LIMIT не может быть отрицательным'
        )
    filters = {
        'date_from': date_from if date_from is not None else utils.get_start_month_date(),
        'date_to': date_to if date_from is not None else utils.get_end_month_date(),
    }
    if id is not None:
        filters['id'] = id
    if group:
        filters['group'] = group
    res = await TransactionsService().get_all(
        uow, user_id=user.id, limit=limit, offset=offset, **filters)
    return res


@router.get('/sum', response_model=float)
async def get_sum_transaction_amounts(
        uow: UOWDep,
        transactions_filters: TransactionsFilters = Depends(
            get_transactions_filters),
        user: User = Depends(current_active_user),
):
    async with uow:
        res = await uow.transactions.calc_sum(
            user_id=user.id, **transactions_filters.model_dump())
        return res
