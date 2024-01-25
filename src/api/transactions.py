from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import src.schemas.transactions
import src.utils.enum_classes
from src.auth.manager import current_active_user
from src.db import core
from src.db.database import get_async_session
from src.db.models import User

router = APIRouter(prefix='/transactions', tags=['Transaction'])


@router.post('/')
async def add_transaction(
        transaction: src.schemas.transactions.TransactionCreate,
        user: User = Depends(current_active_user),
):
    return await core.add_transaction(user.id, transaction)


@router.get('/per_month/')
async def get_amount_group_for_month(
        group: src.utils.enum_classes.OperationGroup,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    return await core.get_transactions_by_group(db, user.id, group)
