'''
File: utils.py
File Created: Friday, 23rd September 2022 11:07:41 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from pydantic import BaseModel
from loguru import logger
from nsa.services.rotator import Rotator
import datetime


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
