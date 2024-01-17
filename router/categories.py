from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.manager import current_active_user
from db import core
from db.database import get_async_session
from db import schemas
from db.models import User, CategoryGroup

router = APIRouter()


# @router.post('/', response_model=schemas.CategoryRead)
@router.post('/')
async def add_category(
        category: schemas.CategoryCreate,
        user: User = Depends(current_active_user),
):
    res = await core.add_category(user.id, category)
    return res


@router.patch('/update')
async def update_category_amount(
        category: schemas.CategoryUpdate,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    return await core.update_category(db, category)


@router.delete('/delete')
async def remove_category(
        category_id: int,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    return await core.remove_category(db, category_id)


@router.get('/all', response_model=list[schemas.CategoryRead])
async def read_categories_by_group(
        group: CategoryGroup,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    return await core.get_categories_by_group(db, user.id, group)
