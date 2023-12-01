import asyncio
import sys
from os import walk

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import db.crud as crud
from db.models import User
import db.schemas as schemas
from db.database import get_db
from auth.manager import fastapi_users, auth_backend, current_active_user
from auth.schemas import UserRead, UserCreate
from db import core
from db.database import async_session
from router.categories import router as router_categories
from router.operations import router as router_operations

app = FastAPI()

app.include_router(
    router_categories,
    prefix='/categories',
    tags=['Category']
)

app.include_router(
    router_operations,
    prefix='/operations',
    tags=['Operation']
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
async def start_app():
    await core.create_tables()


@app.get("/protected-route")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.username}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"


@app.get('/icons')
def get_icons():
    path = 'front-end/src/components/CategoryItem/icons'

    f = []
    for (_, _, filenames) in walk(path):
        for filename in filenames:
            if not filename.startswith('.'):
                f.append(filename)
    return f


@app.get('/icon/{icon_name}')
def get_icon(icon_name: str):
    icons_dir = 'front-end/src/components/CategoryItem/icons/'
    return FileResponse(icons_dir + icon_name)


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get('/balance/')
def get_balance(user_id: int, db: Session = Depends(get_db)):
    balance = crud.get_balance_by_user_id(db, user_id)
    return balance if balance else {'message': 'User not found.'}


@app.post('/balance/', response_model=schemas.Balance)
def set_balance(balance: schemas.BalanceCreate, db: Session = Depends(get_db)):
    return crud.set_balance(db, balance)


@app.get('/balance/{user_id}')
def get_balance(user_id: int):
    if user_id == 12345:
        return 20000
    else:
        return 0


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, use_colors=True)
