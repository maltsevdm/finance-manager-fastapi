from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.manager import current_active_user
from db import schemas
from db import core
from db.database import get_async_session
from db.models import User

router = APIRouter()


@router.post('/add')
async def add_operation(
        operation: schemas.OperationCreate,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    return await core.add_operation(user.id, operation)
