'''
File: authentication.py
File Created: Friday, 16th September 2022 4:47:55 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
import uuid
from typing import Optional
from fastapi_users import FastAPIUsers, BaseUserManager
from fastapi import Depends, Request, APIRouter
from fastapi_users.db import ObjectIDIDMixin
from easydata.database.models import User
from easydata.database.database import get_user_db
import contextlib
from beanie import PydanticObjectId
from fastapi_users.exceptions import UserAlreadyExists
from easydata.models.user import UserCreate, UserRead
from easydata.configs.configs import env_settings

router = APIRouter()

bearer_transport = BearerTransport(tokenUrl="/api/auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=env_settings.JWT_SECRET, lifetime_seconds=env_settings.JWT_LIFETIME)


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = env_settings.JWT_SECRET
    verification_token_secret = env_settings.JWT_SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(
            f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)
current_user = fastapi_users.current_user()


router.include_router(
    fastapi_users.get_auth_router(auth_backend),
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)


async def create_super_user(email: str, password: str, first_name="super", last_name="user"):
    # create a superuser by accessing the db directly
    get_user_db_context = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_context = contextlib.asynccontextmanager(
        get_user_manager)
    super_user = UserCreate(
        # first_name=first_name, last_name=last_name,
        email=email, password=password, is_superuser=True, is_verified=True, first_name=first_name, last_name=last_name)
    async with get_user_db_context() as db_context:
        async with get_user_manager_context(db_context) as user_manager:
            try:
                await user_manager.create(super_user)
            except UserAlreadyExists:
                print(f"User {email} already exists")
