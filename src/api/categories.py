from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.api.dependencies import UOWDep
from src.auth.manager import current_active_user
from src.db import core
from src.db.models import User
from src.schemas.categories import CategorySchemaAdd, CategoryPut, \
    CategoryPatch, CategoryRead
from src.utils.enum_classes import CategoryGroup
from src.services.categories import CategoriesService

router = APIRouter(prefix='/categories', tags=['Category'])


# @router.post('/', response_model=schemas.CategoryRead)
@router.post('/')
async def add_category(
        uow: UOWDep,
        category: CategorySchemaAdd,
        user: User = Depends(current_active_user),
):
    try:
        category = await CategoriesService().add_one(uow, user.id, category)
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail=f'В категории {category.group.value} уже есть категория с '
                   f'именем {category.name}'
        )
    return category


@router.patch('/{id}')
async def patch_category(
        uow: UOWDep,
        id: int,
        category: CategoryPatch,
        user: User = Depends(current_active_user),
):
    res = await CategoriesService().update_one(uow, id, user.id, category)
    return res


@router.delete('/{id}')
async def remove_category(
        uow: UOWDep,
        id: int,
        user: User = Depends(current_active_user),
):
    try:
        res = await CategoriesService().remove_one(uow, user.id, id)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail=f'Нет категории с {id=}')
    return res


@router.get('/', response_model=list[CategoryRead])
async def get_categories(
        uow: UOWDep, user: User = Depends(current_active_user)
):
    res = await CategoriesService().get_categories(uow, user.id)
    return res


@router.get('/{group}', response_model=list[CategoryRead])
async def get_categories_by_group(
        uow: UOWDep,
        group: CategoryGroup,
        user: User = Depends(current_active_user)
):
    res = await CategoriesService().get_categories(uow, user.id, group)
    return res

@router.get('/{id}', response_model=CategoryRead)
async def get_categories_by_id(
        uow: UOWDep,
        id: int,
        user: User = Depends(current_active_user)
):
    res = await CategoriesService().get_categories(uow, user.id, group)
    return res
