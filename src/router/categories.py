from fastapi import APIRouter, Depends

from src.auth.manager import current_active_user
from src.db import core, schemas
from src.db.models import User, CategoryGroup

router = APIRouter()


# @router.post('/', response_model=schemas.CategoryRead)
@router.post('/')
async def add_category(
        category: schemas.CategoryCreate,
        user: User = Depends(current_active_user),
):
    res = await core.add_category(user.id, category)
    return res


@router.put('/')
async def put_category(
        category: schemas.CategoryPut,
        user: User = Depends(current_active_user),
):
    return await core.update_category(user.id, category)


@router.patch('/')
async def patch_category(
        category: schemas.CategoryPatch,
        user: User = Depends(current_active_user),
):
    return await core.patch_category(user.id, category)


@router.delete('/')
async def remove_category(
        category_id: int, user: User = Depends(current_active_user),
):
    return await core.remove_category(user.id, category_id)


@router.get('/', response_model=list[schemas.CategoryRead])
async def get_categories(user: User = Depends(current_active_user)):
    return await core.get_categories(user.id)


@router.get('/{group}', response_model=list[schemas.CategoryRead])
async def get_categories(
        group: CategoryGroup, user: User = Depends(current_active_user)
):
    return await core.get_categories(user.id, group)
