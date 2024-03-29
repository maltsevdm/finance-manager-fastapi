import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound

from src.api.dependencies import UOWDep
from src.auth.manager import current_active_user
from src.db.models import User
from src.schemas.categories import (
    ExpenseIncomeAdd, ExpenseIncomeRead, EiCategoryUpdate)
from src.services.ei_categories import ExpenseIncomeService
from src.utils.enum_classes import ExpenseIncomeGroup

router = APIRouter(prefix='/ei', tags=['expense_income_categories'])


@router.post('/', response_model=ExpenseIncomeRead)
async def add_ei_category(
        uow: UOWDep, category: ExpenseIncomeAdd,
        user: User = Depends(current_active_user)
):
    return await ExpenseIncomeService().add_one(uow, user.id, category)


@router.get('/', response_model=list[ExpenseIncomeRead])
async def get_ei_categories(
        uow: UOWDep,
        group: ExpenseIncomeGroup | None = None,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
        user: User = Depends(current_active_user)
):
    res = await ExpenseIncomeService().get_all(
        uow=uow, user_id=user.id, date_from=date_from, date_to=date_to,
        group=group)
    return res


@router.patch('/{id}', response_model=ExpenseIncomeRead)
async def patch_ei_category(
        uow: UOWDep,
        id: int,
        category: EiCategoryUpdate,
        user: User = Depends(current_active_user),
):
    try:
        res = await ExpenseIncomeService().update_one(uow, id, user.id,
                                                      category)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail=f'Нет категории с {id=}')
    return res


@router.delete('/{id}', response_model=ExpenseIncomeRead)
async def remove_ei_category(
        uow: UOWDep,
        id: int,
        user: User = Depends(current_active_user),
):
    try:
        res = await ExpenseIncomeService().remove_one(uow, user.id, id)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail=f'Нет категории с {id=}')
    return res
