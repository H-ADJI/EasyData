'''
File: models.py
File Created: Tuesday, 20th September 2022 10:31:58 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from datetime import datetime
from fastapi_users.db import BeanieBaseUser
from beanie import Document, PydanticObjectId
from typing import List, Literal, Optional
from nsa.models.scheduling import Interval_trigger, Exact_date_trigger


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
    interval: Optional[Interval_trigger]
    date: Optional[Exact_date_trigger]
    next_run: datetime = None
    input_data: dict
    is_active: bool


class JobExecutionHistory(Document):
    job_id:  PydanticObjectId
    worker_id: str
    retry_count: int
    output_data: dict
    status: Literal["Claimed", "Processing", "Succes", "Failed"]
