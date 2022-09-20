'''
File: models.py
File Created: Tuesday, 20th September 2022 10:31:58 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from datetime import datetime
from fastapi_users.db import BeanieBaseUser
from beanie import Document, PydanticObjectId, Link
from typing import List, Optional
from nsa.models.project import Frequency
from pydantic import BaseModel


class User(BeanieBaseUser[PydanticObjectId]):
    first_name: str
    last_name: str


class Scraping_plan(Document):
    title: str
    description: str
    website: List[str]

    class Settings:
        name = "scraping_plans"


class Scraping_job(Document):
    description: str
    title: str
    schedule_date: datetime
    frequency: Frequency
    scraping_plan: Link[Scraping_plan]

    class Settings:
        name = "scraping_jobs"


class Project(Document):
    description: str
    title: str
    tags: List[str]
    image: str
    owner: Link[User]
    jobs: Optional[List[Link[Scraping_job]]]

    class Settings:
        name = "projects"


class Output_data(Document):
    website: str
    data: dict
    date: datetime
    source_job: Link[Scraping_job]

    class Settings:
        name = "data_nd_analytics"
