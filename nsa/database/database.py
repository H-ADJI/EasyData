import motor.motor_asyncio
from beanie import PydanticObjectId
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from nsa.database.models.user import User
from nsa.configs.configs import env_settings

DB_NAME = env_settings.MONGO_DB_NAME
MONGO_USER = env_settings.MONGO_INITDB_ROOT_USERNAME
MONGO_PASSWORD = env_settings.MONGO_INITDB_ROOT_PASSWORD
MONGO_HOST = env_settings.MONGO_HOST
MONGO_PORT = env_settings.MONGO_PORT


DATABASE_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["nsa"]


async def get_user_db():
    yield BeanieUserDatabase(User)
