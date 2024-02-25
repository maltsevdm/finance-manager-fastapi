from fastapi import APIRouter

from src.api.categories import banks, ei

router = APIRouter(prefix='/categories', include_in_schema=True)

router.include_router(banks.router)
router.include_router(ei.router)


# async def add_category(
#         uow: UOWDep,
#         group: CategoryGroup,
#         category: ExpenseIncomeAdd | BankAdd,
#         user: User,
# ):
#     try:
#         category = await CategoriesService().add_one(uow, user.id, group,
#                                                      category)
#     except IntegrityError as ex:
#         raise HTTPException(
#             status_code=400,
#             detail=f'В категории {category.group.value} уже есть категория с '
#                    f'именем {category.name}'
#         )
#     return category
#
#
# @router.post('/bank/', response_model=BankRead)
# async def add_bank(
#         uow: UOWDep,
#         category: BankAdd,
#         user: User = Depends(current_active_user),
# ):
#     return await add_category(uow, CategoryGroup.bank, category, user)
#
#
# @router.post('/{group}/', response_model=ExpenseIncomeRead)
# async def add_expense_income(
#         uow: UOWDep,
#         group: ExpenseIncomeGroup,
#         category: ExpenseIncomeAdd,
#         user: User = Depends(current_active_user)
# ):
#     group = (CategoryGroup.income if group == ExpenseIncomeGroup.income
#              else CategoryGroup.expense)
#     return await add_category(uow, group, category, user)
#
#
# @router.patch('/{id}', response_model=ExpenseIncomeRead | BankRead)
# async def patch_category(
#         uow: UOWDep,
#         id: int,
#         category: CategoryUpdate,
#         user: User = Depends(current_active_user),
# ):
#     try:
#         res = await CategoriesService().update_one(uow, id, user.id, category)
#     except NoResultFound:
#         raise HTTPException(status_code=400,
#                             detail=f'Нет категории с {id=}')
#     return res
#
#
# @router.delete('/{id}', response_model=ExpenseIncomeRead | BankRead)
# async def remove_category(
#         uow: UOWDep,
#         id: int,
#         user: User = Depends(current_active_user),
# ):
#     try:
#         res = await CategoriesService().remove_one(uow, user.id, id)
#     except NoResultFound:
#         raise HTTPException(status_code=400,
#                             detail=f'Нет категории с {id=}')
#     return res
#
#
# @router.get('/', response_model=list[BankRead | ExpenseIncomeRead])
# async def get_categories(
#         uow: UOWDep,
#         group: Optional[CategoryGroup] = None,
#         id: Optional[int] = None,
#         user: User = Depends(current_active_user)
# ):
#     filters = {'user_id': user.id}
#     if group:
#         filters['group'] = group
#     if id is not None:
#         filters['id'] = id
#     res = await CategoriesService().get_all(uow, **filters)
#     return res
