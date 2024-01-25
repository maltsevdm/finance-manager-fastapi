from fastapi import APIRouter, Depends

import src.schemas.categories
from src.api.dependencies import UOWDep
from src.auth.manager import current_active_user
from src.db import core
from src.db.models import User
from src.utils.enum_classes import CategoryGroup
from src.services.categories import CategoriesService

router = APIRouter(prefix='/categories', tags=['Category'])


# @router.post('/', response_model=schemas.CategoryRead)
@router.post('/')
async def add_category(
        uow: UOWDep,
        category: src.schemas.categories.CategorySchemaAdd,
        user: User = Depends(current_active_user),
):
    category = await CategoriesService().add_category(uow, user.id, category)
    return category


@router.put('/')
async def put_category(
        uow: UOWDep,
        category: src.schemas.categories.CategoryPut,
        user: User = Depends(current_active_user),
):
    res = await CategoriesService().update_category(uow, user.id, category)
    return res


@router.patch('/')
async def patch_category(
        category: src.schemas.categories.CategoryPatch,
        user: User = Depends(current_active_user),
):
    return await core.patch_category(user.id, category)


@router.delete('/')
async def remove_category(
        uow: UOWDep,
        category_id: int,
        user: User = Depends(current_active_user),
):
    res = await CategoriesService().remove_category(uow, user.id, category_id)
    return res


@router.get('/', response_model=list[src.schemas.categories.CategoryRead])
async def get_categories(
        uow: UOWDep,
        user: User = Depends(current_active_user)
):
    res = await CategoriesService().get_categories(uow, user.id)
    return res


@router.get('/{group}',
            response_model=list[src.schemas.categories.CategoryRead])
async def get_categories(
        uow: UOWDep,
        group: CategoryGroup,
        user: User = Depends(current_active_user)
):
    res = await CategoriesService().get_categories(uow, user.id, group)
    return res
