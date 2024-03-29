from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound

from src.api.dependencies import UOWDep, get_banks_filters
from src.auth.manager import current_active_user
from src.db.models import User
from src.schemas.categories import BankAdd, BankRead, BankUpdate, BanksFilters
from src.services.banks import BanksService
from src.utils.enum_classes import BankKindGroup


router = APIRouter(prefix='/banks', tags=['bank'])


@router.post('/', response_model=BankRead)
async def add_bank(
        uow: UOWDep, bank: BankAdd, user: User = Depends(current_active_user)
):
    return await BanksService().add_one(uow, user.id, bank)


@router.get('/', response_model=list[BankRead])
async def get_banks(
        uow: UOWDep,
        banks_filters: BanksFilters = Depends(get_banks_filters),
        user: User = Depends(current_active_user)
):
    res = await BanksService().get_all(
        uow,
        user_id=user.id,
        id=banks_filters.id,
        group=banks_filters.group
    )
    return res


@router.patch('/{id}', response_model=BankRead)
async def patch_bank(
        uow: UOWDep,
        id: int,
        bank: BankUpdate,
        user: User = Depends(current_active_user),
):
    try:
        res = await BanksService().update_one(uow, id, user.id, bank)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail=f'Нет счёта с {id=}')
    return res


@router.delete('/{id}', response_model=BankRead)
async def remove_bank(
        uow: UOWDep,
        id: int,
        user: User = Depends(current_active_user),
):
    try:
        res = await BanksService().remove_one(uow, user.id, id)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail=f'Нет счёта с {id=}')
    return res
