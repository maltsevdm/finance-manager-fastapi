from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.manager import current_active_user
from db import crud, core
from db.database import async_session, get_async_session
from db import schemas
from db.models import User

router = APIRouter()


@router.get('/')
async def read_categories():
    async with async_session() as db:
        return await crud.get_categories(db)


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


@router.delete('/delete')
async def remove_category(
        category: schemas.CategoryRemove,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    await core.remove_category(db, user.id, category)
    return 'Category was successfully deleted.'


@router.get('/all')
async def read_categories_by_group(
        group: str,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    return await core.get_categories_by_group(db, user.id, group)
