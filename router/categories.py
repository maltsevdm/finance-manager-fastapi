from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.manager import current_active_user
from db import core, models
from db.database import async_session, get_async_session
from db import schemas
from db.models import User, CategoryGroup

router = APIRouter()


@router.post('/add')
async def add_category(
        category: schemas.CategoryCreate,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    return await core.add_category(db, user.id, category)


@router.patch('/update')
async def update_category_amount(
        category: schemas.CategoryUpdate,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    await core.update_category_amount(db, user.id, category)
    return 'Category was successfully updated.'


@router.patch('/change_name')
async def change_name(
        group: CategoryGroup,
        old_name: str,
        new_name: str,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    await core.change_category_name(db, user.id, group, old_name, new_name)
    return 'Category name was successfully changed.'


@router.patch('/change_bank_amount')
async def change_bank_amount(
        name: str,
        amount: int,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    await core.change_bank_amount(db, user.id, name, amount)
    return 'Bank amount was successfully changed.'


@router.patch('/change_icon')
async def change_icon(
        group: CategoryGroup,
        name: str,
        icon: str,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    await core.change_category_icon(db, user.id, group, name, icon)
    return 'Category icon was successfully changed.'


@router.delete('/delete')
async def remove_category(
        category: schemas.CategoryRemove,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    await core.remove_category(db, user.id, category)
    return 'Category was successfully deleted.'


@router.get('/all', response_model=list[schemas.CategoryRead])
async def read_categories_by_group(
        group: CategoryGroup,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    return await core.get_categories_by_group(db, user.id, group)
