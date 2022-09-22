
from beanie import PydanticObjectId
from fastapi_users.db import BeanieBaseUser
from pydantic.types import constr


class User(BeanieBaseUser[PydanticObjectId]):
    first_name: str
    last_name: str
