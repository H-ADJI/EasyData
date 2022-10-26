'''
File: conftest.py
File Created: Wednesday, 26th October 2022 10:19:38 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
import pytest
from fastapi import FastAPI
from typing import Generator
from httpx import AsyncClient
from nsa.main import app, get_app
from nsa.configs.configs import env_settings
from motor import motor_asyncio

BASE_URL: str = 'http://localhost:8080/api'


@pytest.fixture(scope='session')
async def mongo_is_ready():
    DB_NAME = env_settings.MONGO_DB_NAME
    MONGO_USER = env_settings.MONGO_INITDB_ROOT_USERNAME
    MONGO_PASSWORD = env_settings.MONGO_INITDB_ROOT_PASSWORD
    MONGO_HOST = env_settings.MONGO_HOST
    MONGO_PORT = env_settings.MONGO_PORT

    DATABASE_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
    client = motor_asyncio.AsyncIOMotorClient(
        DATABASE_URL, uuidRepresentation="standard"
    )
    db = client[DB_NAME]


@pytest.fixture(scope='function')
async def test_client(app: FastAPI) -> Generator:
    async with AsyncClient(app=app, base_url=BASE_URL, follow_redirects=True) as c:
        yield c
