from fastapi import APIRouter

import src.schemas.transactions
from src.db import core

router = APIRouter()


@router.get('/add')
async def add_operation(operation: src.schemas.transactions.TransactionCreate):
    return await core.add_transaction(operation)
