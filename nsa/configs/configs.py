'''
File: configs.py
File Created: Monday, 19th September 2022 12:12:16 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    APP_NAME: str = "News Sites Analytics"
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_HOST: str
    MONGO_PORT: str
    MONGO_DB_NAME: str
    JWT_SECRET: str
    JWT_LIFETIME: int
    # ACTIONS_TIMEOUT: int
    SUPER_USER_EMAIL: EmailStr
    SUPER_USER_PASSWORD: str
    MIN_JOB_SCHEDULING_OFFSET: int
    CELERY_BROKER_URL: str
    DB_POLLING_INTERVAL: int
    MIN_ACCEPTED_INTERVAL: int
    MONGO_TEST_DB_NAME: str
    TESTING: bool

    class Config:
        env_file = "nsa/.env"


env_settings = Settings()
