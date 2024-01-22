from fastapi import APIRouter

from src.db import core, schemas

router = APIRouter()


@router.get('/add')
async def add_operation(operation: schemas.TransactionCreate):
    return await core.add_transaction(operation)
