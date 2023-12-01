from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, FastAPIUsers, exceptions
from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend

from db import core
from db.models import User
from db.core import get_user_db
from auth import schemas

SECRET = "SECRET"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def create(
            self, user_create: schemas.UserCreate, safe: bool = False, request: Optional[Request] = None,
    ):
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)
        await core.add_user_to_balance(created_user.id)

        await self.on_after_register(created_user, request)

        return created_user

    # async def on_after_forgot_password(
    #     self, user: User, token: str, request: Optional[Request] = None
    # ):
    #     print(f"User {user.id} has forgot their password. Reset token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


cookie_transport = CookieTransport(cookie_name='CoinKeeper', cookie_max_age=60 * 60 * 24 * 360)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)
current_active_user = fastapi_users.current_user(active=True)
