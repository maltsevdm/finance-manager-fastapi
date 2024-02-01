import asyncio
import os
import sys
from os import walk

import uvicorn
from fastapi import Depends, FastAPI, APIRouter
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import all_routers
from src.db.models import User
from src.utils.enum_classes import TransactionGroup
from src.db.database import get_async_session
from src.auth.manager import fastapi_users, auth_backend, current_active_user
from src.auth.schemas import UserRead, UserCreate
from src.db import core

app = FastAPI()
router = APIRouter()

for api_router in all_routers:
    router.include_router(api_router)

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

origins = [
    'http://localhost:3000',
    'http://192.168.1.161:3000',
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'OPTIONS', 'DELETE', 'PATCH', 'PUT'],
    allow_headers=['Content-Type', 'Set-Cookie', 'Access-Control-Allow-Headers', 
                   'Access-Control-Allow-Origin', 'Authorization'],
)


# app.mount("/", StaticFiles(directory="static", html=True), name="static")

@router.on_event('startup')
async def start_app():
    await core.create_tables()


@router.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"


@router.get('/icons/all')
def get_icons():
    path = 'icons'

    f = []
    for (_, _, filenames) in walk(path):
        for filename in filenames:
            if not filename.startswith('.'):
                f.append(filename)
    return f


@router.get('/icons/{icon_name}')
def get_icon(icon_name: str):
    path = os.path.join('icons', icon_name)
    return FileResponse(path)


@router.get('/balance/')
def get_balance(user_id: int, db: AsyncSession = Depends(get_async_session)):
    balance = core.get_balance(db, user_id)
    return balance if balance else {'message': 'User not found.'}


@router.get('/general_data')
async def get_general_data(
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    balance = await core.get_balance(db, user.id)
    if balance is None:
        # Создать в категориях для каждой категории новую дату
        await core.prepare_db_for_user(db, user.id)
    balance = await core.get_balance(db, user.id)
    incomes = await core.get_transactions_by_group(db, user.id, TransactionGroup.income)
    expenses = await core.get_transactions_by_group(db, user.id, TransactionGroup.expense)

    return {
        'balance': balance,
        'incomes': incomes,
        'expenses': expenses
    }


app.include_router(
    router,
    prefix='/api'
)

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(app, use_colors=True)
