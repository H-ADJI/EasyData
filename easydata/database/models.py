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
from typing import List, Optional, Union
from easydata.models.scheduling import Exact_date_trigger_read, Interval_trigger_read, CronSchedulingRead
from easydata.models.article import Article, ArticleDetail
from datetime import datetime
from easydata.constants.enums import SchedulingJobStatus, JobHistoryStatus, ScrapingState
from pydantic import validator


class User(BeanieBaseUser[PydanticObjectId]):
    first_name: str
    last_name: str


class Project(Document):
    title: str
    description: str
    url: str
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
    input_data_id: Optional[PydanticObjectId]
    child_id: Optional[PydanticObjectId]
    input_data: Optional[dict]
    interval: Optional[Interval_trigger_read]
    exact_date: Optional[Exact_date_trigger_read]
    cron: Optional[CronSchedulingRead]
    next_run: Optional[datetime]
    status: SchedulingJobStatus

    @validator("next_run")
    def next_run_to_naive(cls, next_run: datetime):
        #  making the date timezone naive in case user sends tz aware datetime
        if next_run:
            next_run = next_run.replace(tzinfo=None)
        return next_run


class JobExecutionHistory(Document):
    job_id:  PydanticObjectId
    created_at: datetime
    claimed_at: Optional[datetime]
    ended_at: Optional[datetime]
    status: JobHistoryStatus
    execution_error: Optional[str]


class ScrapedData(Document):
    job_id: PydanticObjectId
    articles: Union[List[ArticleDetail], List[Article]]
    date_of_scraping: Optional[datetime]
    total: int = 0
    state: ScrapingState = ScrapingState.NOT_STARTED
    took: float = 0
