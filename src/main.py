import asyncio
import sys

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import all_routers
from src.auth.manager import fastapi_users, auth_backend
from src.schemas.users import UserRead, UserCreate, UserUpdate
from src.db import core

app = FastAPI()
router = APIRouter()

for api_router in all_routers:
    router.include_router(api_router)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix='/users',
    tags=['users'],
)

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)

router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix='/auth',
    tags=['auth'],
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


# app.mount('/', StaticFiles(directory='static', html=True), name='static')

@router.on_event('startup')
async def start_app():
    await core.create_tables()


app.include_router(
    router,
    prefix='/api'
)

# if __name__ == '__main__':
#     if sys.platform == 'win32':
#         asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#
#     uvicorn.run(app, use_colors=True)
