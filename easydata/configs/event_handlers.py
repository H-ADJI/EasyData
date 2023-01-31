'''
File: event_handlers.py
File Created: Monday, 3rd October 2022 10:27:21 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from easydata.database.database import db

from beanie import init_beanie
from fastapi import FastAPI
from easydata.api.routes.authentication import create_super_user
from easydata.configs.configs import env_settings
from easydata.services.utils import app_logger
from easydata.database.models import Project, User, ScrapingPlan, JobScheduling
from typing import Coroutine


async def _startup(app: FastAPI):
    app_logger.info("Server Startup")
    await init_beanie(
        database=db,
        document_models=[Project, User, ScrapingPlan, JobScheduling],
    )
    await create_super_user(email=env_settings.SUPER_USER_EMAIL, password=env_settings.SUPER_USER_PASSWORD)


async def _shutdown(app: FastAPI):
    app_logger.info("Server Shutdown")


def startup_handler(app: FastAPI) -> Coroutine:
    """Startup Routine
    """
    async def startup() -> None:
        #logger.info("Running app start handler.")
        await _startup(app)
    return startup


def shutdown_handler(app: FastAPI) -> Coroutine:
    """Shutdown Routine
    """
    async def shutdown() -> None:
        #logger.info("Running app shutdown handler.")
        await _shutdown(app)
    return shutdown
