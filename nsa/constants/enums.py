'''
File: enums.py
File Created: Thursday, 29th September 2022 2:56:51 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from enum import Enum


class SchedulingJobStatus(str, Enum):
    WAITING = "WAITING"
    DONE = "DONE"
    FAILED = "FAILED"
    RECCURING = "RECCURING"


class JobHistoryStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
