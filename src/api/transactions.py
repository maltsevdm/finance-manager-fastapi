from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound

from src.api.dependencies import UOWDep
from src.auth.manager import current_active_user
from src.db import core
from src.db.models import User
from src.schemas.transactions import TransactionCreate
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
        transation_id: int,
        user: User = Depends(current_active_user),
):
    try:
        res = await TransactionsService().remove_one(uow, transation_id,
                                                     user.id)
    except (ValueError, PermissionError) as ex:
        raise HTTPException(400, ex)
    return res


@router.put('/{id}')
async def update_transaction(
        uow: UOWDep,
        transation_id: int,
        transaction: TransactionCreate,
        user: User = Depends(current_active_user),
):
    try:
        res = await TransactionsService().update_one(
            uow, transation_id, transaction, user.id
        )
    except (ValueError, PermissionError) as ex:
        return HTTPException(400, ex)
    return res

# @router.get('/per_month/')
# async def get_amount_group_for_month(
#         group: src.utils.enum_classes.TransactionGroup,
#         user: User = Depends(current_active_user),
#         db: AsyncSession = Depends(get_async_session)
# ):
#     return await core.get_transactions_by_group(db, user.id, group)
