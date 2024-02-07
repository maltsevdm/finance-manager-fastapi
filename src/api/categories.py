from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.api.dependencies import UOWDep
from src.auth.manager import current_active_user
from src.db.models import User
from src.schemas.categories import CategoryAdd, CategoryUpdate, CategoryRead
from src.utils.enum_classes import CategoryGroup
from src.services.categories import CategoriesService

router = APIRouter(prefix='/categories', tags=['category'])


@router.post('/', response_model=CategoryRead)
async def add_category(
        uow: UOWDep,
        category: CategoryAdd,
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


@router.patch('/{id}', response_model=CategoryRead)
async def patch_category(
        uow: UOWDep,
        id: int,
        category: CategoryUpdate,
        user: User = Depends(current_active_user),
):
    try:
        res = await CategoriesService().update_one(uow, id, user.id, category)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail=f'Нет категории с {id=}')
    return res


@router.delete('/{id}', response_model=CategoryRead)
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
        uow: UOWDep,
        group: Optional[CategoryGroup] = None,
        id: Optional[int] = None,
        user: User = Depends(current_active_user)
):
    filters = {'user_id': user.id}
    if group:
        filters['group'] = group
    if id is not None:
        filters['id'] = id
    res = await CategoriesService().get_categories(uow, **filters)
    return res
