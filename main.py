import asyncio
import os
import sys
from os import walk

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, APIRouter
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from db.models import User, CategoryGroup, OperationGroup
import db.schemas as schemas
from db.database import get_db, get_async_session
from auth.manager import fastapi_users, auth_backend, current_active_user
from auth.schemas import UserRead, UserCreate
from db import core
from db.database import async_session
from router.categories import router as router_categories
from router.transactions import router as router_operations

app = FastAPI()
router = APIRouter()

router.include_router(
    router_categories,
    prefix='/categories',
    tags=['Category']
)

router.include_router(
    router_operations,
    prefix='/transactions',
    tags=['Transaction']
)

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
    'http://192.168.1.160:3000',
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'OPTIONS', 'DELETE', 'PATCH', 'PUT'],
    # allow_methods=['*'],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
    # allow_headers=['*']
)


# app.mount("/", StaticFiles(directory="static", html=True), name="static")

@router.on_event('startup')
async def start_app():
    await core.create_tables()


@router.get("/protected-route")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.username}"


@router.get('/test/all')
def get_test():
    return 'Hello, World'


@router.get('/test/user')
def get_test_user(user: User = Depends(current_active_user)):
    return f'Protected route for {user.username}'


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
    incomes = await core.get_transactions_by_group(db, user.id, OperationGroup.income)
    expenses = await core.get_transactions_by_group(db, user.id, OperationGroup.expense)

    return {'balance': balance, 'incomes': incomes, 'expenses': expenses}


app.include_router(
    router,
    prefix='/api'
)

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.1.160", port=8000, use_colors=True)
