'''
File: utils.py
File Created: Friday, 23rd September 2022 11:07:41 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
import pathlib
from pydantic import BaseModel
from loguru import logger
from nsa.services.rotator import Rotator
import datetime
import os
from contextlib import contextmanager


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
