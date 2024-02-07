from fastapi import APIRouter, Depends, HTTPException
from psycopg.errors import CheckViolation, ForeignKeyViolation
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.api.dependencies import UOWDep
from src.auth.manager import current_active_user
from src.db.models import User
from src.schemas.debts import DebtRead, DebtAdd, DebtUpdate
from src.services.depts import DebtsService

router = APIRouter(prefix='/debts', tags=['debt'])


@router.post('/', response_model=DebtRead)
async def add_debt(
        uow: UOWDep,
        debt: DebtAdd,
        user: User = Depends(current_active_user),
):
    try:
        debt = await DebtsService().add_one(uow, user.id, debt)
    except IntegrityError as ex:
        if isinstance(ex.orig, CheckViolation):
            detail = 'Сумма долга не может быть отрицательной.'
        elif isinstance(ex.orig, ForeignKeyViolation):
            detail = f'Нет счёта с id={debt.bank_id}'
        else:
            print(ex)
            detail = 'Долг не добавлен. Неизвестная ошибка'
        raise HTTPException(status_code=400, detail=detail)
    return debt


@router.delete('/{id}', response_model=DebtRead)
async def remove_debt(
        uow: UOWDep,
        id: int,
        user: User = Depends(current_active_user),
):
    try:
        debt = await DebtsService().remove_one(uow, user.id, id)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail=f'Нет долга с id={id}')
    return debt


@router.get('/', response_model=list[DebtRead])
async def get_debts(
        uow: UOWDep,
        user: User = Depends(current_active_user),
):
    debts = await DebtsService().get_all(uow, user_id=user.id)
    return debts


@router.patch('/{id}', response_model=DebtRead)
async def update_debt(
        id: int,
        debt: DebtUpdate,
        uow: UOWDep,
        user: User = Depends(current_active_user)
):
    debt = await DebtsService().update_one(uow, id, user.id, debt)
    return debt
