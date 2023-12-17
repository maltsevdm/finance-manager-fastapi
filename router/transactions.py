from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.manager import current_active_user
from db import schemas, models
from db import core
from db.database import get_async_session
from db.models import User

router = APIRouter()


@router.post('/add')
async def add_transaction(
        operation: schemas.TransactionCreate,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    return await core.add_operation(db, user.id, operation)

@router.get('/per_month/')
async def get_amount_group_for_month(
        group: models.OperationGroup,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    return await core.get_transactions_by_group(db, user.id, group)