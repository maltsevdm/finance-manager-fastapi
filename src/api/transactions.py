import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound

from src.api.dependencies import UOWDep
from src.auth.manager import current_active_user
from src.db import core
from src.db.models import User
from src.schemas.transactions import TransactionCreate, TransactionUpdate
from src.services.transactions import TransactionsService

router = APIRouter(prefix='/transactions', tags=['Transaction'])


@router.post('/')
async def add_transaction(
        uow: UOWDep,
        transaction: TransactionCreate,
        user: User = Depends(current_active_user),
):
    try:
        res = await TransactionsService().add_one(uow, user.id, transaction)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail='Одна из категорий не существует')
    except ValueError:
        raise HTTPException(status_code=400,
                            detail='Неверное направление транзакции')
    return res


@router.delete('/{id}')
async def remove_transaction(
        uow: UOWDep,
        id: int,
        user: User = Depends(current_active_user),
):
    try:
        res = await TransactionsService().remove_one(uow, id, user.id)
    except (ValueError, PermissionError) as ex:
        raise HTTPException(400, ex)
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
            uow, id, transaction, user.id
        )
    except (ValueError, PermissionError) as ex:
        return HTTPException(400, ex)
    return res

@router.get('/{date_from}-{date_to}')
async def get_amount_group_for_month(
        date_from: datetime.date,
        date_to: datetime.date,
        user: User = Depends(current_active_user),
):
    return await core.get_transactions_by_group(db, user.id, group)
