'''
File: enums.py
File Created: Thursday, 29th September 2022 2:56:51 pm
Author: KHALIL HADJI 
-----
Copyright:  H-adji 2022
'''
from enum import Enum


class SchedulingJobStatus(str, Enum):
    WAITING = "WAITING"
    WAITING_FOR_PARENT = "WAITING_FOR_PARENT"
    READY = "READY"
    DONE = "DONE"
    FAILED = "FAILED"
    REOCCURING = "REOCCURING"


class JobHistoryStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ScrapingState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    ABORTED = "ABORTED"
    FINISHED = "FINISHED"
