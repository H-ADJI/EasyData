'''
File: models.py
File Created: Tuesday, 20th September 2022 10:31:58 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from datetime import datetime
from pydantic import Field
from fastapi_users.db import BeanieBaseUser
from beanie import Document, PydanticObjectId
from typing import List, Literal, Optional
from nsa.models.scheduling import Exact_date_trigger_read, Exact_date_trigger_write, Interval_trigger_write, Interval_trigger_read
from datetime import datetime, timedelta
from nsa.configs.configs import env_settings
from nsa.constants.enums import SchedulingJobStatus, JobHistoryStatus


class User(BeanieBaseUser[PydanticObjectId]):
    first_name: str
    last_name: str


class Project(Document):
    description: str
    title: str
    tags: Optional[List[str]]
    image: Optional[str]
    owner_id:  PydanticObjectId


class ScrapingPlan(Document):
    owner_id:  PydanticObjectId
    website: str
    title: str
    plan: dict


class JobScheduling(Document):
    owner_id:  PydanticObjectId
    plan_id: PydanticObjectId
    interval: Optional[Interval_trigger_read]
    exact_date: Optional[Exact_date_trigger_read]
    next_run: float
    input_data: dict
    status: SchedulingJobStatus


class JobExecutionHistory(Document):
    job_id:  PydanticObjectId
    worker_id: str
    created_at: datetime
    claimed_at: datetime
    ended_at: datetime
    data_id: dict
    status: JobHistoryStatus
