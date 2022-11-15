'''
File: utils.py
File Created: Friday, 23rd September 2022 11:07:41 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from pydantic import BaseModel
from loguru import logger
from nsa.services.async_sync.async_sync import AioThread
from nsa.services.rotator import Rotator
import pytz
import datetime
import os
from contextlib import contextmanager
from nsa.configs.configs import env_settings
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from nsa.database.database import DATABASE_URL
from nsa.database.models import Project, User, ScrapingPlan, JobScheduling, JobExecutionHistory, ScrapedData
DB_NAME = env_settings.MONGO_DB_NAME


def none_remover(model: BaseModel) -> dict:
    original = model.dict()
    filtered = {k: v for k, v in original.items() if v is not None}
    original.clear()
    original.update(filtered)
    return original


def get_logging() -> logger:
    """Prepare logger with general configuration

    Returns:
        logger: Configured logger instance
    """
    # Rotate file if over 500 MB or at midnight every day
    rotator: Rotator = Rotator(size=5e+8, at=datetime.time(0, 0, 0))
    # design rotators
    logger.add(
        "./log/file_{time}.log", rotation=rotator.should_rotate)
    return logger


app_logger = get_logging()


def detect_tasks(project_root: str = os.path.basename(os.getcwd()), extra: str = None) -> tuple:
    """Detect tasks dynamically without having to define much in the config file
    """
    if extra:
        project_root = os.path.join(project_root, extra)

    # list of tasks
    tasks = []
    with change_tmp('..'):
        # full file path

        file_path = os.path.join(project_root, 'tasks')
        logger.info(f'Celery task detection at {file_path}')
        for root, dirs, files in os.walk(file_path):
            for filename in files:
                if os.path.basename(root) == 'tasks':
                    if filename != '__init__.py' and filename.endswith('.py'):
                        task = os.path.join(root, filename)\
                            .replace('/', '.')\
                            .replace('.py', '')

                        tasks.append(task)
    return tuple(tasks)


@contextmanager
def change_tmp(path) -> None:
    """changing the current working directory for the duration of a context
    """

    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def construct_aio_threading(aio_thread: AioThread) -> None:
    """construct the aio threading for async/await communication
    """
    # check if Thread had already started
    if not aio_thread.is_alive():
        # start the new created thread
        aio_thread.start()
        # wait for its creation to complete
        aio_thread.event.wait()


def destruct_aio_threading(aio_thread: AioThread) -> None:
    """Setup the aio threading for async/await communication
    """
    # check if thread already alive before distroying it
    if aio_thread.is_alive():
        # finalizing the aoi thread
        aio_thread.finalize()
        # free the space holden by the aio_thread
        aio_thread = None


async def db_session():
    # init beanie doesnt work

    client = AsyncIOMotorClient(
        DATABASE_URL, uuidRepresentation="standard"
    )

    db = client[DB_NAME]

    await init_beanie(
        database=db,
        document_models=[Project, User, ScrapingPlan,
                         JobScheduling, JobExecutionHistory, ScrapedData],
    )


def simulate_user_current_time(user_tz: str):
    user_tz = pytz.timezone(user_tz)
    # this simulate the current datetime from the user perspective but removes time zone info
    now = datetime.datetime.now().astimezone(tz=user_tz).replace(tzinfo=None)
    return now
